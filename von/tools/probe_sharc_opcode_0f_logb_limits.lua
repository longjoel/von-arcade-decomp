-- Exercise opcode 0x0f near the signed LOGB exponent-distance limits.

local frame = 0
local index = 0
local space
local log_file
local vectors = {
    { 0x3f800000, 0x4f800000, 0, 0 }, -- helper (2^32,1)
    { 0x4f800000, 0x3f800000, 0, 0 }, -- helper (1,2^32)
    { 0x3f800000, 0x5f800000, 0, 0 }, -- helper (2^64,1)
    { 0x5f800000, 0x3f800000, 0, 0 }, -- helper (1,2^64)
    { 0x3f800000, 0x7e800000, 0, 0 }, -- helper (2^126,1)
    { 0x7e800000, 0x3f800000, 0, 0 }, -- helper (1,2^126)
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function inject(vector)
    space:write_u32(0x00884000, 8)
    space:write_u32(0x00884000, 0x0f)
    for _, word in ipairs(vector) do space:write_u32(0x00884000, word) end
    index = index + 1
    log("probe: injected logb-limit-index=" .. index)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0F_LOG") or
                "vonj-sharc-opcode-0f-logb-limits.log", "w"))
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
