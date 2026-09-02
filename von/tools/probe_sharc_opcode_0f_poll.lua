-- Isolate opcode 0x0f and poll the host response FIFO directly.

local frame = 0
local next_vector = 1
local pending_vector = 0
local space
local log_file

local vectors = {
    { 0x3f800000, 0x00000000, 0x00000000, 0x00000000 }, -- (x,y)=(0,1)
    { 0x00000000, 0x3f800000, 0x00000000, 0x00000000 }, -- (x,y)=(1,0)
    { 0x3f800000, 0x3f800000, 0x00000000, 0x00000000 }, -- diagonal
    { 0x00000000, 0xbf800000, 0x00000000, 0x00000000 }, -- (x,y)=(-1,0)
    { 0xbf800000, 0x00000000, 0x00000000, 0x00000000 }, -- (x,y)=(0,-1)
    { 0x3f800000, 0xbf800000, 0x00000000, 0x00000000 }, -- (x,y)=(-1,1)
    { 0x00000000, 0x00000000, 0x00000000, 0x00000000 }, -- zero vector
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function inject(vector_index)
    local vector = vectors[vector_index]
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000000f)
    for _, word in ipairs(vector) do space:write_u32(0x00884000, word) end
    pending_vector = vector_index
    log("probe: injected opcode=0x0f vector-index=" .. vector_index)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0F_POLL_LOG") or
                "vonj-sharc-opcode-0f-poll.log", "w"))
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
                " vector-index=" .. pending_vector .. " frame=" .. frame)
        else
            log("probe: response-poll-error=" .. tostring(data))
        end
        pending_vector = 0
    end
    if frame >= 2650 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
