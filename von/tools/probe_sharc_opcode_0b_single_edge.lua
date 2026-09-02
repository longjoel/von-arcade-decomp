-- Single-vector opcode-0b edge probe with a long post-boot settle window.

local frame = 0
local lane = 0
local response_ready = false
local selected_case = os.getenv("VON_SHARC_0B_SINGLE_CASE") or "zero"
local payloads = {
    zero = { 0, 0, 0, 0, 0, 0, 0, 0, 0 },
    baseline = { 0x40400000, 0x40800000, 0x41400000, 0, 0, 0,
                 0x3f800000, 0x3f800000, 0 },
}
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0B_SINGLE_EDGE_LOG") or
                "vonj-sharc-opcode-0b-single-edge.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 1800 then
        space:write_u32(0x00884000, 0x00000008)
        space:write_u32(0x00884000, 0x0000000b)
        local payload = assert(payloads[selected_case], "unknown opcode-0b case")
        -- The dispatcher reaches the service after consuming the first word
        -- following the opcode. The nine payload words are therefore sent
        -- contiguously here.
        for _, word in ipairs(payload) do space:write_u32(0x00884000, word) end
        log("probe: injected case=" .. selected_case)
    end
    if frame >= 2300 and not response_ready then
        local fifo_empty = space:read_u32(0x00980004)
        log(string.format("probe: fifo-control=0x%08x", fifo_empty))
        response_ready = fifo_empty == 0
    end
    if response_ready and lane < 3 then
        lane = lane + 1
        log(string.format("probe: response lane=%d value=0x%08x", lane,
            space:read_u32(0x00884000)))
    end
    if frame >= 2400 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
