-- Serialize a state reset, one opcode-0x2c packet, and a state readback.
-- The handlers are deliberately separated by frames so a long-running
-- service cannot consume the following command words as its own payload.

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
            log_file = assert(io.open(os.getenv("VON_SHARC_2C_DISPATCH_LOG") or
                "vonj-sharc-opcode-2c-dispatch.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x29)
        word(0)
        word(0)
        word(0)
        word(0)
        log("probe: reset via opcode-0x29")
    end
    if frame == 900 then
        header(0x2c)
        for _ = 1, 6 do word(0) end
        log("probe: opcode-0x2c neutral six-word packet")
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
