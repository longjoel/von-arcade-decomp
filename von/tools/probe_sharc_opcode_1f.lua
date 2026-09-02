-- Directly exercise the SHARC dispatcher entry for opcode 0x1f.
-- This is a diagnostic stimulus, not part of the game driver.

local TARGET_FRAMES = 2400
local INJECT_FRAME = 1800
local frame = 0
local vector_index = 0
local space
local log_file

local function log(message)
    if log_file then
        log_file:write(message .. "\n")
        log_file:flush()
    end
end

local vectors = {
    { "zero",       0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000 },
    { "unit-x",     0x3f800000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000 },
    { "3-4-12",     0x40400000, 0x00000000, 0x40800000, 0x00000000, 0x41400000, 0x00000000 },
    { "fractional", 0x3fa00000, 0x3f400000, 0xc0300000, 0x3f400000, 0x3f000000, 0xbeffffff },
}

local function inject(vector)
    -- The dispatcher first consumes a standalone 0x08 marker and resets its
    -- service-state index, then reads the raw table selector.
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000001f)

    for index = 2, #vector do
        local word = vector[index]
        space:write_u32(0x00884000, word)
    end
    vector_index = vector_index + 1
    log("probe: injected vector=" .. vector[1] .. " index=" .. vector_index)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_1F_LOG") or
                "vonj-sharc-opcode-1f-probe.log", "w"))
            log("probe: start")
        end
    end
    if not space then
        return
    end
    if frame >= INJECT_FRAME and (frame - INJECT_FRAME) % 120 == 0 then
        local index = math.floor((frame - INJECT_FRAME) / 120) + 1
        if vectors[index] then
            inject(vectors[index])
        end
    end
    if frame >= TARGET_FRAMES then
        log("probe: complete")
        if log_file then
            log_file:close()
        end
        manager.machine:exit()
    end
end)
