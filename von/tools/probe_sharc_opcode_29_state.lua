-- Exercise opcode 0x29, then read back the complete persistent state.

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
            log_file = assert(io.open(os.getenv("VON_SHARC_29_STATE_LOG") or
                "vonj-sharc-opcode-29-state.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x29)
        word(0x41200000)
        word(0x41a00000)
        word(0x41f00000)
        word(0x00000000)
        header(0x11)
        log("probe: translation=(10,20,30), signed-angle=0")
    end
    if frame == 700 then
        header(0x29)
        word(0x41200000)
        word(0x41a00000)
        word(0x41f00000)
        word(0x00004000)
        header(0x11)
        log("probe: translation=(10,20,30), signed-angle=0x4000")
    end
    if frame == 800 then
        header(0x29)
        word(0x41200000)
        word(0x41a00000)
        word(0x41f00000)
        word(0x0000c000)
        header(0x11)
        log("probe: translation=(10,20,30), signed-angle=0xc000")
    end
    if frame >= 900 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
