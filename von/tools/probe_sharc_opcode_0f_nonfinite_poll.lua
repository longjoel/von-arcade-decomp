-- Exercise non-normal opcode-0x0f packets and poll the host FIFO directly.

local frame = 0
local next_vector = 1
local pending_vector = 0
local space
local copro
local log_file
local vectors = {
    { 0x3f800000, 0x7fc00000, 0x00000000, 0x00000000 }, -- F0=+qNaN, F1=1
    { 0x7fc00000, 0x3f800000, 0x00000000, 0x00000000 }, -- F0=1, F1=+qNaN
    { 0x3f800000, 0x7f800000, 0x00000000, 0x00000000 }, -- F0=+inf, F1=1
    { 0x7f800000, 0x3f800000, 0x00000000, 0x00000000 }, -- F0=1, F1=+inf
    { 0x3f800000, 0x00000001, 0x00000000, 0x00000000 }, -- F0=min subnormal, F1=1
    { 0x00000001, 0x3f800000, 0x00000000, 0x00000000 }, -- F0=1, F1=min subnormal
    { 0x3f800000, 0xff800000, 0x00000000, 0x00000000 }, -- F0=-inf, F1=1
    { 0xffc00000, 0x3f800000, 0x00000000, 0x00000000 }, -- F0=1, F1=-qNaN
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function state_value(name)
    if not copro or not copro.state[name] then return "unavailable" end
    local ok, value = pcall(function() return copro.state[name].value end)
    return ok and string.format("0x%08x", value) or "unreadable"
end

local function inject(vector_index)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000000f)
    for _, word in ipairs(vectors[vector_index]) do space:write_u32(0x00884000, word) end
    pending_vector = vector_index
    log("probe: injected nonfinite-index=" .. vector_index)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        copro = manager.machine.devices[":copro_adsp"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0F_NONFINITE_POLL_LOG") or
                "vonj-sharc-opcode-0f-nonfinite-poll.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame >= 1800 and (frame - 1800) % 120 == 0 and next_vector <= #vectors then
        inject(next_vector)
        next_vector = next_vector + 1
    end
    if pending_vector ~= 0 and frame >= 1810 + ((pending_vector - 1) * 120) then
        local ok, data = pcall(function() return space:read_u32(0x00884000) end)
        if ok then
            log("probe: response-poll=" .. tostring(data) ..
                " vector-index=" .. pending_vector .. " frame=" .. frame ..
                " astat=" .. state_value("ASTAT") .. " stky=" .. state_value("STKY"))
        else
            log("probe: response-poll-error=" .. tostring(data))
        end
        pending_vector = 0
    end
    if frame >= 3000 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
