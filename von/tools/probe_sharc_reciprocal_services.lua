-- Exercise SHARC reciprocal/division services 0x03-0x04.

local frame = 0
local index = 0
local space
local log_file
local requests = {
    { 0x03, 0x40000000, 0x3f800000 }, -- 2.0 / 1.0
    { 0x03, 0x3f800000, 0x40000000 }, -- 1.0 / 2.0
    { 0x03, 0xc0000000, 0x3f800000 }, -- -2.0 / 1.0
    { 0x04, 0x40000000, 0x3f800000 }, -- residual-style paired service
    { 0x04, 0x3f800000, 0x40000000 },
    { 0x04, 0x40000000, 0x40000000 },
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function inject(request)
    space:write_u32(0x00884000, 8)
    space:write_u32(0x00884000, request[1])
    space:write_u32(0x00884000, request[2])
    space:write_u32(0x00884000, request[3])
    index = index + 1
    log(string.format("probe: injected reciprocal-index=%d opcode=%02x", index, request[1]))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_RECIPROCAL_LOG") or
                "vonj-sharc-reciprocal-services.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame >= 600 and (frame - 600) % 120 == 0 and index < #requests then
        inject(requests[index + 1])
    end
    if frame >= 630 and (frame - 630) % 120 == 0 and index > 0 then
        local response = space:read_u32(0x00884000)
        log(string.format("probe: response=0x%08x", response))
    end
    if frame >= 1320 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
