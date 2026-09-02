-- Exercise opcode 0x2c with a neutral six-word packet, then read state.

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
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_2C_LOG") or
                "vonj-sharc-opcode-2c-zero.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x10)
        header(0x2c)
        for _ = 1, 6 do word(0) end
        header(0x11)
        log("probe: opcode-0x2c six-word neutral packet")
    end
    if frame == 900 then
        header(0x10)
        header(0x2c)
        word(0x00003c00)
        for _ = 1, 5 do word(0) end
        header(0x11)
        log("probe: opcode-0x2c packed-field-R0-half-1")
    end
    if frame == 1200 then
        header(0x10)
        header(0x2c)
        for _ = 1, 3 do word(0) end
        word(0x00000040)
        word(0)
        word(0)
        header(0x11)
        log("probe: opcode-0x2c signed-low-byte-R13-0x40")
    end
    if frame == 1500 then
        header(0x10)
        header(0x2c)
        for _ = 1, 4 do word(0) end
        word(0x00000040)
        word(0)
        header(0x11)
        log("probe: opcode-0x2c signed-low-byte-R14-0x40")
    end
    if frame == 1800 then
        header(0x10)
        header(0x2c)
        for _ = 1, 5 do word(0) end
        word(0x00000040)
        header(0x11)
        log("probe: opcode-0x2c signed-low-byte-R15-0x40")
    end
    if frame == 2100 then
        header(0x10)
        header(0x2c)
        word(0x00004000)
        for _ = 1, 5 do word(0) end
        header(0x11)
        log("probe: opcode-0x2c packed-field-R0-half-2")
    end
    if frame == 2400 then
        header(0x10)
        header(0x2c)
        word(0x3f800000)
        word(0)
        word(0)
        word(0)
        word(0)
        word(0)
        header(0x11)
        log("probe: opcode-0x2c float-field-R0-1")
    end
    if frame >= 2700 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
