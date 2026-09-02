-- Directly exercise opcode 0x0c with boundary-oriented vectors.
-- This is a diagnostic stimulus for comparing SHARC and C arithmetic.

local TARGET_FRAMES = 1500
local INJECT_FRAME = 600
local frame = 0
local index = 0
local space
local log_file

local vectors = {
    { "unit-next",  0x3f800001, 0, 0 },
    { "asym-next",  0x3f800000, 0x3f800001, 0 },
    { "cancel",     0x3f800001, 0xbf800000, 0 },
    { "large-x",    0x4b800000, 0, 0 },
    { "large-mix",  0x4b800000, 0x4b800000, 0x4b800001 },
}

local function log(message)
    if log_file then
        log_file:write(message .. "\n")
        log_file:flush()
    end
end

local function inject(vector)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000000c)
    for position = 2, #vector do
        space:write_u32(0x00884000, vector[position])
    end
    index = index + 1
    log(string.format("probe: injected vector=%s index=%d", vector[1], index))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0C_ROUNDING_LOG") or
                "vonj-sharc-opcode-0c-rounding.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame >= INJECT_FRAME and (frame - INJECT_FRAME) % 120 == 0 then
        local vector_number = math.floor((frame - INJECT_FRAME) / 120) + 1
        if vectors[vector_number] then inject(vectors[vector_number]) end
    end
    if frame >= TARGET_FRAMES then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
