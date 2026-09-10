-- Deterministic per-cabinet stimulus for scripts/test-twin.sh.
-- The two processes use the same script, but each process has its own
-- isolated state directory and independently injects its own coin/start.

local seconds = tonumber(os.getenv("VON_TWIN_SECONDS") or "60")
local log_path = os.getenv("VON_TWIN_LOG") or "von-twin-lua.log"
local log = assert(io.open(log_path, "w"))
local frame = 0
local fields = {}
local space
local last_hash
local release_at = {}
local preflight = os.getenv("VON_TWIN_PREFLIGHT") == "1"
local role = os.getenv("VON_TWIN_ROLE") or "slave"
local preflight_done = false
local preflight_failed = false
local fields_resolved = false
local completion_frame
local probe = os.getenv("VON_TWIN_PROBE") == "1"
local probe_until = 0
local probe_taps = {}
local probe_pcs = {}
local cpu_dev
local probe_dump = os.getenv("VON_TWIN_PROBE_DUMP") == "1"

local names = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "1 Player Start" },
    test = { ":IN0", "Service Mode" },
    service = { ":IN0", "Service 1" },
    up = { ":IN1", "P1 Left Stick/Up" },
    shot = { ":IN1", "P1 Left Shot" },
}

local function write(message)
    log:write(message .. "\n")
    log:flush()
end

local function pulse(field, duration)
    if field then
        field:set_value(1)
        release_at[field] = frame + duration
    end
end

local function preflight_action(at, field, duration)
    if frame == at then
        write("twin: preflight press " .. field .. " frame=" .. frame)
        pulse(fields[field], duration or 8)
    end
end

local function run_preflight()
    if not preflight or preflight_done or not fields.test or not fields.service then
        return
    end
    -- Menu order documented by VO16/VO20: six Service presses select Game
    -- Assignments from the initial Memory Test entry.
    preflight_action(120, "test")
    for i = 0, 5 do preflight_action(240 + i * 60, "service") end
    preflight_action(660, "test")
    -- Game Assignments: four Service presses select Network Link Attribute.
    for i = 0, 3 do preflight_action(780 + i * 60, "service") end
    preflight_action(1080, "test")
    -- The documented values cycle No Link -> Master -> Slave.  Select the
    -- desired role from the factory/default No Link value.
    preflight_action(1140, "test")
    if role == "slave" then preflight_action(1200, "test") end
    -- Move to Exit, commit the assignment, and allow network checking to run.
    for i = 0, 13 do preflight_action(1320 + i * 60, "service") end
    preflight_action(2220, "test")
    if frame >= 2220 then
        write("twin: preflight complete role=" .. role)
        preflight_done = true
    end
end

local function resolve()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then return false end
    cpu_dev = cpu
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    for key, spec in pairs(names) do
        local port = manager.machine.ioport.ports[spec[1]]
        fields[key] = port and port.fields[spec[2]] or nil
        write("twin: field " .. key .. "=" .. (fields[key] and "resolved" or "missing") ..
            " port=" .. spec[1] .. " name=" .. spec[2])
    end
    local required = space ~= nil and fields.coin ~= nil and fields.start ~= nil
    if preflight then
        required = required and fields.test ~= nil and fields.service ~= nil
    end
    return required
end

local function hash_tiles()
    if not space then return nil end
    local hash = 2166136261
    for i = 0, 4095 do
        hash = ((hash ~ space:read_u16(0x01000000 + i * 2)) * 16777619) % 4294967296
    end
    return hash
end

local function probe_end(tag)
    for addr, tap in pairs(probe_taps) do
        pcall(function() space:uninstall_read_tap(tap) end)
        local pcs = {}
        for pc, count in pairs(probe_pcs[addr] or {}) do
            pcs[#pcs + 1] = string.format("%s(x%d)", pc, count)
        end
        table.sort(pcs)
        write(string.format("twin: probe tap %08x %s readers=%s", addr, tag,
            table.concat(pcs, " ")))
    end
    probe_taps = {}
    probe_pcs = {}
end

local function probe_begin()
    if not probe or not space then return end
    for _, addr in ipairs({ 0x503c08, 0x503c10, 0x503bbc }) do
        probe_pcs[addr] = {}
        local ok, tap = pcall(function()
            return space:install_read_tap(addr, addr + 3,
                string.format("twinprobe%08x", addr),
                function(offset, data, mask)
                    local pc = "?"
                    local ok_pc, value = pcall(function()
                        return cpu_dev.state["CURPC"].value
                    end)
                    if ok_pc and type(value) == "number" then
                        pc = string.format("0x%x", value)
                    end
                    local seen = probe_pcs[addr]
                    seen[pc] = (seen[pc] or 0) + 1
                    return data
                end)
        end)
        if ok and tap then probe_taps[addr] = tap end
    end
end

local function probe_telemetry(tag)
    if not probe or not space then return end
    local words = {}
    for _, addr in ipairs({ 0x503c08, 0x503c0c, 0x503c10, 0x503c14, 0x503bbc }) do
        words[#words + 1] = string.format("%08x", space:read_u32(addr))
    end
    write(string.format("twin: probe tele %s f%d %s", tag, frame,
        table.concat(words, " ")))
end

local function probe_snapshot(tag)
    if not probe_dump or not space then return end
    local path = string.format("%s.%s.%04d.txt", log_path, tag, frame)
    local out = assert(io.open(path, "w"))
    for addr = 0x500000, 0x506000 - 4, 4 do
        out:write(string.format("%08x %08x\n", addr, space:read_u32(addr)))
    end
    out:close()
    write("twin: probe snapshot " .. tag .. " frame=" .. frame)
end

emu.register_periodic(function()
    frame = frame + 1
    for field, until_frame in pairs(release_at) do
        if frame >= until_frame then
            field:clear_value()
            release_at[field] = nil
        end
    end
    if not fields_resolved and frame % 30 == 1 then
        fields_resolved = resolve()
        if fields_resolved then
            write("twin: fields resolved")
        end
    end
    if preflight and not fields_resolved and not preflight_failed and frame >= 120 then
        preflight_failed = true
        write("twin: preflight failed: required input fields were not resolved")
        manager.machine:exit()
        return
    end
    if preflight_failed then return end
    run_preflight()
    local credit_frame = preflight and 2700 or 900
    local start_frame = preflight and 3300 or 1500
    local battle_frame = preflight and 3600 or 1800
    if frame == credit_frame then
        write("twin: credit frame=" .. frame)
        pulse(fields.coin, 8)
    elseif frame == start_frame then
        write("twin: start frame=" .. frame)
        pulse(fields.start, 8)
    elseif frame >= battle_frame and frame % 120 == 0 then
        write("twin: battle-input frame=" .. frame)
        pulse(fields.up, 45)
        if frame % 240 == 0 then
            pulse(fields.shot, 8)
            if probe then
                probe_end("pre")
                probe_snapshot("pre")
                probe_begin()
                probe_until = frame + 60
                write("twin: probe shot frame=" .. frame)
            end
        end
    end
    if probe and frame >= battle_frame and frame < probe_until and frame % 5 == 0 then
        probe_telemetry("shot")
    elseif probe and probe_until > 0 and frame == probe_until then
        probe_snapshot("post")
        probe_end("post")
    end
    if frame >= battle_frame and frame % 60 == 0 then
        local current = hash_tiles()
        if current and current ~= last_hash then
            write("twin: battle-screen-change frame=" .. frame)
            last_hash = current
        end
    end
    if frame >= seconds * 60 and not completion_frame then
        write("twin: complete frames=" .. frame)
        completion_frame = frame
    elseif completion_frame and frame >= completion_frame + 600 then
        log:close()
        manager.machine:exit()
    end
end)
