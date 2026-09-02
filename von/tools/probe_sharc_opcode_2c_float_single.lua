-- Isolate opcode 0x2c's direct floating-point R0/R1/R2 triple.

local frame = 0
local space
local log_file

local function word(value)
    space:write_u32(0x00884000, value)
end

local function header(opcode)
    word(0x00000008)
    word(opcode)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_2C_FLOAT_LOG") or
                "vonj-sharc-opcode-2c-float-single.log", "w"))
            log_file:write("probe: start\n")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x10)
        header(0x2c)
        word(0x3f800000)
        word(0x40000000)
        word(0x40400000)
        word(0)
        word(0)
        word(0)
        header(0x11)
        log_file:write("probe: direct-float=(1,2,3)\n")
        log_file:flush()
    end
    if frame >= 900 then
        log_file:write("probe: complete\n")
        log_file:close()
        manager.machine:exit()
    end
end)
