-- Directly exercise opcode 0x1f with values chosen around float boundaries.
-- This is a diagnostic stimulus for comparing SHARC rounding with the C model.

local TARGET_FRAMES = 1500
local INJECT_FRAME = 600
local frame = 0
local index = 0
local space
local log_file

local vectors = {
    { "sqrt-2",       0x3f800000, 0, 0x3f800000, 0, 0, 0 },
    { "sqrt-3",       0x3f800000, 0, 0x3f800000, 0, 0x3f800000, 0 },
    { "nextafter-1",  0x3f800001, 0, 0, 0, 0, 0 },
    { "nextafter-2",  0x3f800000, 0, 0x3f800001, 0, 0, 0 },
    { "large",        0x4b800000, 0, 0x4b800000, 0, 0x4b800000, 0 },
}

local function log(message)
    if log_file then
        log_file:write(message .. "\n")
        log_file:flush()
    end
end

local function inject(vector)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000001f)
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
            log_file = assert(io.open(os.getenv("VON_SHARC_1F_ROUNDING_LOG") or
                "vonj-sharc-opcode-1f-rounding.log", "w"))
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
