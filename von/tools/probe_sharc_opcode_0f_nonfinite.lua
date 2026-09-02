-- Exercise non-normal float payloads through opcode 0x0f and helper 0x20d68.
-- The opcode forms F1=(word 1-word 3), F0=(word 2-word 4), so each entry
-- below is {desired F1, desired F0, 0, 0}.

local frame = 0
local index = 0
local space
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

local function inject(vector)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000000f)
    for _, word in ipairs(vector) do space:write_u32(0x00884000, word) end
    index = index + 1
    log("probe: injected nonfinite-index=" .. index)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0F_LOG") or
                "vonj-sharc-opcode-0f-nonfinite.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame >= 1800 and (frame - 1800) % 120 == 0 and index < #vectors then
        inject(vectors[index + 1])
    end
    if frame >= 3000 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
