-- Poll normalized-vector edge results directly from the host FIFO.

local frame = 0
local index = 0
local response_index = 0
local space
local log_file
local vectors = {
    { 0x00000000, 0x00000000, 0x00000000, "zero" },
    { 0x80000000, 0x00000000, 0x00000000, "negative-zero" },
    { 0x00000001, 0x00000000, 0x00000000, "denormal" },
    { 0x7f800000, 0x00000000, 0x00000000, "infinity" },
    { 0x7fc00000, 0x00000000, 0x00000000, "nan" },
    { 0x3f800000, 0x7f800000, 0x00000000, "one-infinity" },
    { 0x00000000, 0x7f800000, 0x00000000, "zero-infinity" },
    { 0xff800000, 0x00000000, 0x00000000, "negative-infinity" },
    { 0x7f800000, 0x7f800000, 0x00000000, "two-infinity" },
    { 0x3f800000, 0x00000001, 0x00000000, "one-denormal" },
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function inject(vector)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000000c)
    space:write_u32(0x00884000, vector[1])
    space:write_u32(0x00884000, vector[2])
    space:write_u32(0x00884000, vector[3])
    index = index + 1
    response_index = 0
    log(string.format("probe: injected index=%d label=%s", index, vector[4]))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0C_EDGES_LOG") or
                "vonj-sharc-opcode-0c-edges.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame >= 1800 and (frame - 1800) % 110 == 0 and index < #vectors then
        inject(vectors[index + 1])
    end
    if index > 0 and response_index < 3 and frame >= 1810 + ((index - 1) * 110) then
        local response = space:read_u32(0x00884000)
        response_index = response_index + 1
        log(string.format("probe: response index=%d lane=%d value=0x%08x", index,
            response_index, response))
    end
    if frame >= 3000 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
