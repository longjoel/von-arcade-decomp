-- Queue identity initialization, zero-angle opcode 0x14, and readback as
-- one FIFO burst so normal gameplay cannot interleave between the operations.

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
                "von-sharc-rotation-snapshot.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        command(0x10)
        command(0x14, 0x00000000)
        command(0x11)
    end
    if frame >= 900 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
