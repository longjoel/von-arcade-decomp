-- Hash the live SHARC program memory at several frames to test whether the
-- uploaded program is constant across game phases (opcode context question).
local LOG = os.getenv("VON_PM_LOG") or "/tmp/opencode/pm.log"
local frame = 0
local sharc, pm, logf

local function find_sharc()
    for _, dev in pairs(manager.machine.devices) do
        if dev.shortname == "adsp21062" then return dev end
    end
    return manager.machine.devices[":copro_adsp"]
end

local function hash_range(space, base, count)
    local h = 2166136261
    for i = 0, count - 1 do
        local ok, v = pcall(function() return space:read_u32(base + i * 4) end)
        if ok and type(v) == "number" then
            h = (h ~ v) & 0xffffffff
            h = (h * 16777619) & 0xffffffff
        end
    end
    return h
end

local FRAMES = { 300, 600, 900, 1800, 3600, 7200 }

emu.register_periodic(function()
    frame = frame + 1
    if not sharc then
        sharc = find_sharc()
        if sharc then
            pm = sharc.spaces[":program"] or sharc.spaces["program"]
            logf = assert(io.open(LOG, "w"))
            logf:write("probe: sharc=" .. tostring(sharc) .. " pm=" .. tostring(pm) .. "\n")
            logf:flush()
        end
    end
    if not pm then return end
    for _, f in ipairs(FRAMES) do
        if frame == f then
            local h = hash_range(pm, 0, 0x1000)
            logf:write(string.format("pm frame=%d hash=%08x\n", frame, h))
            logf:flush()
        end
    end
    if frame >= 7300 then
        logf:close()
        manager.machine:exit()
    end
end)
