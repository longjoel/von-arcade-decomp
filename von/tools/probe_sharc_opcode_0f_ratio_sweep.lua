-- Broader finite-ratio sweep for helper 0x20d68.
-- The trace hook in MAME records the helper's final F15 word.

local frame = 0
local index = 0
local space
local log_file
local vectors = {
    { 0x40400000, 0x3f000000, 0x00000000, 0x00000000 }, -- helper (0.5, 3)
    { 0x3f000000, 0x40400000, 0x00000000, 0x00000000 }, -- helper (3, 0.5)
    { 0x40a00000, 0x3e800000, 0x00000000, 0x00000000 }, -- helper (0.25, 5)
    { 0x3e800000, 0x40a00000, 0x00000000, 0x00000000 }, -- helper (5, 0.25)
    { 0x40400000, 0xbf000000, 0x00000000, 0x00000000 }, -- helper (-0.5, 3)
    { 0xbf000000, 0x40400000, 0x00000000, 0x00000000 }, -- helper (3, -0.5)
    { 0x40c00000, 0xbf800000, 0x00000000, 0x00000000 }, -- helper (-1, 6)
    { 0xbf800000, 0x40c00000, 0x00000000, 0x00000000 }, -- helper (6, -1)
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function inject(vector)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000000f)
    for _, word in ipairs(vector) do space:write_u32(0x00884000, word) end
    index = index + 1
    log("probe: injected ratio-sweep-index=" .. index)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0F_RATIO_SWEEP_LOG") or
                "vonj-sharc-opcode-0f-ratio-sweep.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame >= 1800 and (frame - 1800) % 100 == 0 and index < #vectors then
        inject(vectors[index + 1])
    end
    if frame >= 2750 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
