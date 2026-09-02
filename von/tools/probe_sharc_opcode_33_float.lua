-- Isolate opcode 0x33's direct translation fields.

local frame = 0
local space
local log_file

local function word(value) space:write_u32(0x00884000, value) end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_33_LOG") or
                "vonj-sharc-opcode-33-float.log", "w"))
            log_file:write("probe: start\n")
        end
    end
    if not space then return end
    if frame == 600 then
        word(0x00000008); word(0x00000010)
        word(0x00000008); word(0x00000033)
        word(0x3f800000); word(0x40000000); word(0x40400000)
        word(0); word(0)
        word(0x00000008); word(0x00000011)
        log_file:write("probe: direct-float=(1,2,3), signed-fields=(0,0)\n")
        log_file:flush()
    end
    if frame >= 900 then
        log_file:write("probe: complete\n"); log_file:close(); manager.machine:exit()
    end
end)
