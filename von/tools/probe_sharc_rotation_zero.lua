-- Validate the state-transform boundary with identity, zero-angle rotation,
-- and state readback. Opcode 0x14 consumes one signed-16 angle word.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function command(opcode, payload)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, opcode)
    if payload then space:write_u32(0x00884000, payload) end
    log(string.format("probe: command=0x%02x", opcode))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_ROTATION_LOG") or
                "von-sharc-rotation-zero.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 1800 then command(0x10) end
    if frame == 1920 then command(0x14, 0x00000000) end
    if frame == 2040 then command(0x11) end
    if frame >= 2250 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
