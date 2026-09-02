-- Early isolated zero-vector probe for opcode 0x0f.

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
            log_file = assert(io.open(os.getenv("VON_0F_ZERO_LOG") or
                "vonj-sharc-opcode-0f-zero-early.log", "w"))
            log_file:write("probe: start\n")
        end
    end
    if not space then return end
    if frame == 600 then
        word(0x00000008); word(0x0000000f)
        word(0); word(0); word(0); word(0)
        log_file:write("probe: injected zero vector\n"); log_file:flush()
    end
    if frame >= 1000 then
        log_file:write("probe: complete\n"); log_file:close(); manager.machine:exit()
    end
end)
