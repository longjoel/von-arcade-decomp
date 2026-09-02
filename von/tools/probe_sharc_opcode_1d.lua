-- Probe the two-input signed-fixed-point multiply service at opcode 0x1d.
-- The first word is a signed 16-bit angle; the second word is an IEEE-754
-- multiplier carried through the SHARC register-file alias.

local frame = 0
local space
local log_file
local requests = {
    { 0x00004000, 0x3f800000 }, -- sin(pi/2) * 1.0
    { 0x00002000, 0x40000000 }, -- sin(pi/4) * 2.0
    { 0xffffc000, 0x3f000000 }, -- sin(-pi/2) * 0.5
    { 0x00007fff, 0x3f800000 }, -- endpoint rounding
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function send(angle, multiplier)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000001d)
    space:write_u32(0x00884000, angle)
    space:write_u32(0x00884000, multiplier)
    log(string.format("probe: opcode=0x1d angle=0x%08x multiplier=0x%08x", angle, multiplier))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_1D_LOG") or
                "von-sharc-opcode-1d.log", "w"))
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
