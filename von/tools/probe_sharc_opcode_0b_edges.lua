-- Poll normalized-cross-product edge results directly from the host FIFO.

local frame = 0
local index = 0
local response_index = 0
local response_ready = false
local last_injection_frame = -10000
local space
local log_file
local vectors = {
    { 0, 0, 0, 0, 0, 0, 0, 0, 0, "zero" },
    { 0x3f800000, 0, 0, 0x3f800000, 0, 0, 0x3f800000, 0, 0, "degenerate" },
    { 0, 0x3f800000, 0, 0, 0, 0, 0x3f800000, 0, 0, "negative-z-axis" },
    { 0x7fc00000, 0, 0, 0, 0, 0, 0x3f800000, 0, 0, "nan-endpoint" },
    { 0x7f800000, 0, 0, 0, 0, 0, 0x3f800000, 0, 0, "infinite-endpoint" },
    { 0x00000001, 0, 0, 0, 0, 0, 0x3f800000, 0, 0, "denormal-endpoint" },
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function inject(vector)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000000b)
    for lane = 1, 9 do space:write_u32(0x00884000, vector[lane]) end
    index = index + 1
    response_index = 0
    response_ready = false
    last_injection_frame = frame
    log(string.format("probe: injected index=%d label=%s", index, vector[10]))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0B_EDGES_LOG") or
                "vonj-sharc-opcode-0b-edges.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame >= 1800 and not (response_index > 0 and response_index < 3) and
        response_index == 3 and index < #vectors and frame >= last_injection_frame + 140 then
        inject(vectors[index + 1])
    end
    if index == 0 and frame >= 1800 then
        inject(vectors[1])
    end
    if index > 0 and response_index < 3 and frame >= last_injection_frame + 50 then
        if not response_ready then
            local fifo_empty = space:read_u32(0x00980004)
            response_ready = fifo_empty == 0
            if not response_ready then
                log(string.format("probe: response-wait index=%d fifo-control=0x%08x",
                    index, fifo_empty))
            end
        end
        if response_ready then
            local response = space:read_u32(0x00884000)
            response_index = response_index + 1
            log(string.format("probe: response index=%d lane=%d value=0x%08x", index,
                response_index, response))
            response_ready = false
        end
    end
    if frame >= 2750 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
