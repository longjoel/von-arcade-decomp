-- Exercise opcode 0x0f across large exponent distances.

local frame = 0
local index = 0
local space
local log_file
local vectors = {
    { 0x3f800000, 0x41800000, 0, 0 }, -- helper (8,1)
    { 0x41800000, 0x3f800000, 0, 0 }, -- helper (1,8)
    { 0x3f800000, 0x42800000, 0, 0 }, -- helper (64,1)
    { 0x42800000, 0x3f800000, 0, 0 }, -- helper (1,64)
    { 0x3f800000, 0x43800000, 0, 0 }, -- helper (256,1)
    { 0x43800000, 0x3f800000, 0, 0 }, -- helper (1,256)
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function inject(vector)
    space:write_u32(0x00884000, 8)
    space:write_u32(0x00884000, 0x0f)
    for _, word in ipairs(vector) do space:write_u32(0x00884000, word) end
    index = index + 1
    log("probe: injected exponent-edge-index=" .. index)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0F_LOG") or
                "vonj-sharc-opcode-0f-exponent-edges.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame >= 1800 and (frame - 1800) % 120 == 0 and index < #vectors then
        inject(vectors[index + 1])
    end
    if frame >= 2600 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
