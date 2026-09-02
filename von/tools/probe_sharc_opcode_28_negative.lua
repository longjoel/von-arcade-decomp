-- Short isolated probe for opcode 0x28's negative-depth gate.

local frame = 0
local space
local log_file

local function word(value)
    space:write_u32(0x00884000, value)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_28_NEGATIVE_LOG") or
                "vonj-sharc-opcode-28-negative.log", "w"))
            log_file:write("probe: start\n"); log_file:flush()
        end
    end
    if not space then return end
    if frame == 600 then
        word(0x00000008); word(0x00000010)
        word(0x00000008); word(0x00000028)
        for _, value in ipairs({0, 0, 0xbf800000, 0x40000000, 0x40000000}) do word(value) end
        log_file:write("probe: case=negative-depth\n"); log_file:flush()
    elseif frame >= 840 then
        log_file:write("probe: complete\n"); log_file:close()
        manager.machine:exit()
    end
end)
