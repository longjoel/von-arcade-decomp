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
        if frame % 240 == 0 then pulse(fields.shot, 8) end
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
