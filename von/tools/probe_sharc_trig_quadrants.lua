-- Probe the signed fixed-point sine/cosine services across their quadrants.

local frame = 0
local space
local log_file
local values = {
    0x00000000, 0x00002000, 0x00004000, 0x00006000,
    0x00007fff, 0xffff8000, 0xffffa000, 0xffffc000,
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function send(opcode, value)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, opcode)
    space:write_u32(0x00884000, value)
    log(string.format("probe: opcode=0x%02x input=0x%08x", opcode, value))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_TRIG_LOG") or
                "von-sharc-trig-quadrants.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end

    local offset = frame - 600
    if offset >= 0 and offset % 120 == 0 then
        local index = offset / 120 + 1
        if index <= #values then
            send(0x1b, values[index])
            send(0x1c, values[index])
        end
    end
    if frame >= 1650 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
