-- Install the ROM's quarter-turn Z rotation, update the persistent translation
-- tail through opcode 0x2f with packed (1,2,3), then read it back with 0x20.

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
            log_file = assert(io.open(os.getenv("VON_SHARC_2F_ROTATION_LOG") or
                "von-sharc-opcode-2f-rotation.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x10)
        header(0x16)
        word(0x00004000)
        header(0x2f)
        word(0x00003c00)
        word(0x00004000)
        word(0x00004200)
        header(0x20)
        log("probe: rotation-z=quarter-turn packed-vector=1,2,3 tail-readback")
    end
    if frame >= 900 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
