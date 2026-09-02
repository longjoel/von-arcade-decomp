-- Isolated post-boot probe for the SHARC opcode-0x04 residual service.

local frame = 0
local index = 0
local space
local log_file
local requests = {
    { 0x3f9df3b6, 0x3f333333 }, -- arbitrary positive pair
    { 0xbf9df3b6, 0x3f333333 }, -- signed numerator
    { 0x3fd9999a, 0x3eaaaaab }, -- 1.7 / 1/3
    { 0x3eaaaaab, 0x3fd9999a }, -- 1/3 / 1.7
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function send(first, second)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x00000004)
    space:write_u32(0x00884000, first)
    space:write_u32(0x00884000, second)
    index = index + 1
    log(string.format("probe: opcode=0x04 index=%d first=0x%08x second=0x%08x", index, first, second))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_04_LOG") or
                "von-sharc-opcode-04.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    local offset = frame - 600
    if offset >= 0 and offset % 100 == 0 and index < #requests then
        send(requests[index + 1][1], requests[index + 1][2])
    end
    if offset >= 10 and (offset - 10) % 100 == 0 and index > 0 then
        local response = space:read_u32(0x00884000)
        log(string.format("probe: response=0x%08x", response))
    end
    if frame >= 1050 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
