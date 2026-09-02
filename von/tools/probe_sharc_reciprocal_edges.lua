-- Capture exception-boundary behavior for SHARC reciprocal services.

local frame = 0
local index = 0
local responses = 0
local space
local log_file
local requests = {
    { 0x03, 0x3f800000, 0x00000000, "1/0" },
    { 0x03, 0x00000000, 0x3f800000, "0/1" },
    { 0x03, 0x7f800000, 0x3f800000, "+inf/1" },
    { 0x03, 0x3f800000, 0x7f800000, "1/+inf" },
    { 0x03, 0x7fc00000, 0x3f800000, "nan/1" },
    { 0x03, 0x3f800000, 0x7fc00000, "1/nan" },
    { 0x03, 0x00000001, 0x3f800000, "denormal/1" },
    { 0x04, 0x3f800000, 0x00000000, "residual-1/0" },
    { 0x04, 0x3f800000, 0x7f800000, "residual-1/inf" },
    { 0x04, 0x7fc00000, 0x3f800000, "residual-nan/1" },
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
    log(string.format("probe: injected index=%d opcode=0x%02x first=0x%08x second=0x%08x label=%s",
        index, request[1], request[2], request[3], request[4]))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_RECIPROCAL_EDGES_LOG") or
                "vonj-sharc-reciprocal-edges.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame >= 600 and (frame - 600) % 100 == 0 and index < #requests then
        inject(requests[index + 1])
    end
    if frame >= 610 and (frame - 610) % 100 == 0 and responses < index then
        local response = space:read_u32(0x00884000)
        responses = responses + 1
        log(string.format("probe: response=0x%08x", response))
    end
    if frame >= 1700 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
