-- Probe the cosine-shaped signed-fixed-point conversion service at opcode 0x1c.

local frame = 0
local space
local log_file
local values = { 0x00000000, 0x00004000, 0x00007fff, 0xffff8000 }

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function send(value)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000001c)
    space:write_u32(0x00884000, value)
    log(string.format("probe: opcode=0x1c input=0x%08x", value))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_1C_LOG") or
                "von-sharc-opcode-1c.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    local offset = frame - 600
    if offset >= 0 and offset % 100 == 0 then
        local index = offset / 100 + 1
        if index <= #values then send(values[index]) end
    end
    if frame >= 1050 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
