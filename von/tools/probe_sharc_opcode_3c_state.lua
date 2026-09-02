-- Exercise opcode 0x3c with vector (3,4,12), then read back the complete
-- persistent state through opcode 0x11.  The existing MAME output hook covers
-- the twelve readback words at 0x2029e..0x202c4.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function header(opcode)
    word(0x00000008)
    word(opcode)
    log(string.format("probe: header=0x%02x", opcode))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_3C_STATE_LOG") or
                "von-sharc-opcode-3c-state.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x10)
        header(0x3c)
        word(0x40400000)
        word(0x40800000)
        word(0x41400000)
        header(0x11)
        log("probe: normalized-state-input=(3,4,12)")
    end
    if frame >= 900 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
