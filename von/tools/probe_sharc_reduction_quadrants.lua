-- Sweep signed fixed-point sine/cosine services through all 16-bit quadrants.

local frame = 0
local index = 0
local space
local log_file
local values = {
    0x00000000, 0x00001000, 0x00002000, 0x00003000,
    0x00004000, 0x00005000, 0x00006000, 0x00007000,
    0xffff8000, 0xffff9000, 0xffffa000, 0xffffb000,
    0xffffc000, 0xffffd000, 0xffffe000, 0xfffff000,
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function send(opcode, value)
    space:write_u32(0x00884000, 8)
    space:write_u32(0x00884000, opcode)
    space:write_u32(0x00884000, value)
    log(string.format("probe: index=%d opcode=%02x input=%08x", index + 1, opcode, value))
    index = index + 1
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_REDUCTION_QUADRANT_LOG") or
                "vonj-sharc-reduction-quadrants.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    local offset = frame - 600
    if offset >= 0 and offset % 100 == 0 and index < #values * 2 then
        local value = values[(index % #values) + 1]
        local opcode = index < #values and 0x1b or 0x1c
        send(opcode, value)
    end
    if frame >= 3900 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
