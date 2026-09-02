-- Install diagonal (2,3,4) through opcode 0x13, then validate opcode 0x1a
-- against vector (1,2,3), all in one FIFO burst.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function header(opcode)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, opcode)
    log(string.format("probe: header=0x%02x", opcode))
end

local function word(value)
    space:write_u32(0x00884000, value)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_1A_SCALED_LOG") or
                "von-sharc-service-1a-scaled.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x10)
        header(0x13)
        word(0x40000000)
        word(0x40400000)
        word(0x40800000)
        header(0x1a)
        word(0x3f800000)
        word(0x40000000)
        word(0x40400000)
        log("probe: matrix-scale=2,3,4 vector=1,2,3")
    end
    if frame >= 900 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
