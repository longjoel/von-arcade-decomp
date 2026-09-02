-- Sweep opcode 0x45's two signed-16 angle inputs and scale.

local frame = 0
local index = 0
local space
local log_file

local vectors = {
    { "origin", 0x0000, 0x0000, 0x3f800000 },
    { "x-quarter", 0x4000, 0x0000, 0x40000000 },
    { "y-quarter", 0x0000, 0x4000, 0x40000000 },
    { "diagonal", 0x2000, 0x2000, 0x40000000 },
    { "negative-a", 0xe000, 0x2000, 0x3fc00000 },
    { "negative-b", 0x2000, 0xe000, 0x3fc00000 },
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function inject(vector)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x00000045)
    space:write_u32(0x00884000, vector[2])
    space:write_u32(0x00884000, vector[3])
    space:write_u32(0x00884000, vector[4])
    index = index + 1
    log(string.format("probe: index=%d name=%s a=%04x b=%04x scale=%08x",
        index, vector[1], vector[2], vector[3], vector[4]))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_45_SWEEP_LOG") or
                "vonj-sharc-opcode-45-sweep.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame >= 100 and (frame - 100) % 100 == 0 then
        local vector_number = math.floor((frame - 100) / 100) + 1
        if vectors[vector_number] then inject(vectors[vector_number]) end
    end
    if frame >= 800 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
