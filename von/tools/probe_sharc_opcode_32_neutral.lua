-- Exercise opcode 0x32 with an identity-seeded neutral packet.

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
            log_file = assert(io.open(os.getenv("VON_SHARC_32_LOG") or
                "vonj-sharc-opcode-32-neutral.log", "w"))
            log_file:write("probe: start\n")
        end
    end
    if not space then return end
    if frame == 600 then
        word(0x00000008); word(0x00000010)
        word(0x00000008); word(0x00000032)
        for _ = 1, 9 do word(0) end
        word(0x00000008); word(0x00000011)
        log_file:write("probe: identity-seeded nine-word neutral packet\n")
        log_file:flush()
    end
    if frame >= 900 then
        log_file:write("probe: complete\n")
        log_file:close()
        manager.machine:exit()
    end
end)
