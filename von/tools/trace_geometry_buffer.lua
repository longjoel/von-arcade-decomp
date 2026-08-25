-- Capture the generated host geometry table at 0x00509ba0.
-- The table is produced by i960 routine 0x28b80 during startup.

local LOG_PATH = os.getenv("VON_GEOMETRY_BUFFER_LOG") or "geometry-buffer.log"
local DUMP_PATH = os.getenv("VON_GEOMETRY_BUFFER_DUMP") or "geometry-buffer.hex"
local SAMPLE_WORDS = 0x2000
local frame = 0
local previous_hash = nil
local dumps = 0

local log_file = assert(io.open(LOG_PATH, "w"))
local cpu = manager.machine.devices[":maincpu"]
local space = cpu.spaces["program"]

local function log(message)
    log_file:write(message .. "\n")
    log_file:flush()
end

local function sample()
    local hash = 2166136261
    for index = 0, SAMPLE_WORDS - 1 do
        local value = space:read_u32(0x00509ba0 + index * 4)
        hash = (hash ~ value) * 16777619 % 4294967296
    end
    return hash
end

local function dump(path, hash)
    local dump_file = assert(io.open(path, "w"))
    dump_file:write(string.format("# frame=%d hash=%08x words=%x\n",
        frame, hash, SAMPLE_WORDS))
    for index = 0, SAMPLE_WORDS - 1 do
        local value = space:read_u32(0x00509ba0 + index * 4)
        dump_file:write(string.format("%04x %08x\n", index, value))
    end
    dump_file:close()
end

log("geometry buffer probe start")
emu.register_periodic(function()
    frame = frame + 1
    if frame % 30 == 0 then
        local hash = sample()
        if hash ~= previous_hash then
            previous_hash = hash
            log(string.format("frame=%d hash=%08x", frame, hash))
            if dumps < 4 then
                local path = string.format("%s.%d", DUMP_PATH, dumps)
                dump(path, hash)
                log("dump=" .. path)
                dumps = dumps + 1
            end
        end
    end
    if frame >= 600 then
        log("geometry buffer probe complete")
        log_file:close()
        manager.machine:exit()
    end
end)
