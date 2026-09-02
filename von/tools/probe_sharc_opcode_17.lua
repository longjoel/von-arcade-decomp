-- Minimal opcode-0x17 streamed-table probe.  The 0x0d setup establishes the
-- table/state bases before the three-word 0x17 header.

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
    log(string.format("probe: command=0x%02x payload=%08x", opcode,
        payload or 0))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_17_LOG") or
                "von-sharc-opcode-17.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        command(0x0d, 0x00000000)
        command(0x17, 0x00000000)
        command(0x17, 0x00000000)
        command(0x17, 0x00000000)
    end
    if frame >= 900 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
