-- Exercise SHARC scalar services 0x00-0x02 while tracing FIFO/persistent lanes.

local frame = 0
local index = 0
local space
local log_file
local requests = {
    { 0x00, 0x3f800000, 0x40000000 }, -- add: 1.0, 2.0
    { 0x01, 0x40000000, 0x3f800000 }, -- subtract: 2.0, 1.0
    { 0x02, 0x3f000000, 0x40000000 }, -- multiply: 0.5, 2.0
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
    log(string.format("probe: injected scalar-index=%d opcode=%02x", index, request[1]))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_SCALAR_LOG") or
                "vonj-sharc-scalar-services.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame >= 1800 and (frame - 1800) % 180 == 0 and index < #requests then
        inject(requests[index + 1])
    end
    if frame >= 2450 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
