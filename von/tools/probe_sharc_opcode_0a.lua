-- Probe the two-input floating-point fixed-angle service at opcode 0x0a.

local frame = 0
local space
local log_file
local requests = {
    { 0x3f800000, 0x00000000 }, -- atan2(1, 0)
    { 0x00000000, 0x3f800000 }, -- atan2(0, 1)
    { 0x3f800000, 0x3f800000 }, -- atan2(1, 1)
    { 0xbf800000, 0x3f800000 }, -- atan2(-1, 1)
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function send(first, second)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000000a)
    space:write_u32(0x00884000, first)
    space:write_u32(0x00884000, second)
    log(string.format("probe: opcode=0x0a first=0x%08x second=0x%08x", first, second))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0A_LOG") or
                "von-sharc-opcode-0a.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    local offset = frame - 600
    if offset >= 0 and offset % 100 == 0 then
        local index = offset / 100 + 1
        if index <= #requests then
            send(requests[index][1], requests[index][2])
        end
    end
    if offset >= 10 and (offset - 10) % 100 == 0 then
        local response = space:read_u32(0x00884000)
        log(string.format("probe: response=0x%08x", response))
    end
    if frame >= 1050 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
