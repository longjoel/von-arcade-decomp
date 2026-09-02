-- Initialize the persistent matrix to identity, then exercise opcode 0x28.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_28_LOG") or
                "vonj-sharc-opcode-28-identity.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        word(0x00000008); word(0x00000010)
        log("probe: initialized identity state")
    end
    if frame == 760 then
        word(0x00000008); word(0x00000028)
        for _, value in ipairs({0, 0, 0x3f800000, 0x40000000, 0x40000000}) do word(value) end
        log("probe: case=identity-unit-z-r5-r6-2")
    end
    if frame >= 1200 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
