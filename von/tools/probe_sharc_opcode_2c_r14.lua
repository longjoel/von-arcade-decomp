-- Isolate opcode 0x2c's R14 signed angle after a serialized identity reset.

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
            log_file = assert(io.open(os.getenv("VON_SHARC_2C_R14_LOG") or
                "vonj-sharc-opcode-2c-r14.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x10)
        log("probe: reset via opcode-0x10")
    end
    if frame == 900 then
        header(0x2c)
        word(0)
        word(0)
        word(0)
        word(0)
        word(0x00000040)
        word(0)
        log("probe: opcode-0x2c R14=0x0040")
    end
    if frame == 1200 then
        header(0x11)
        log("probe: opcode-0x11 state readback")
    end
    if frame >= 1500 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
