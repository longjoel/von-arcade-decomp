-- Probe helper 0x20de1 with a simple known plane while varying the caller
-- coordinates.  The selected record is P0=(0,0,0), P1=(2,0,0),
-- P2=(1,1,0), P3=(0,0,1), so the normal helper result is y=x+z.

local frame = 0
local fifo_space
local data_space
local log_file
local case_index = 0
local pending

local cases = {
    { 0x3f800000, 0x3f800000, "base P2=(1,1,0)" },
    { 0x3f800000, 0x3f800000, "P2=(1,2,0)" },
    { 0x3f800000, 0x3f800000, "P3=(0,1,1)" },
    { 0x3f800000, 0x3f800000, "P1=(2,1,0)" },
}

local records = {
    {
        0x00000000, 0x00000000, 0x00000000,
        0x40000000, 0x00000000, 0x00000000,
        0x3f800000, 0x3f800000, 0x00000000,
        0x00000000, 0x00000000, 0x3f800000,
    },
    {
        0x00000000, 0x00000000, 0x00000000,
        0x40000000, 0x00000000, 0x00000000,
        0x3f800000, 0x40000000, 0x00000000,
        0x00000000, 0x00000000, 0x3f800000,
    },
    {
        0x00000000, 0x00000000, 0x00000000,
        0x40000000, 0x00000000, 0x00000000,
        0x3f800000, 0x3f800000, 0x00000000,
        0x00000000, 0x3f800000, 0x3f800000,
    },
    {
        0x00000000, 0x00000000, 0x00000000,
        0x40000000, 0x3f800000, 0x00000000,
        0x3f800000, 0x3f800000, 0x00000000,
        0x00000000, 0x00000000, 0x3f800000,
    },
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    fifo_space:write_u32(0x00884000, value)
end

local function command(opcode, payload)
    word(0x00000008)
    word(opcode)
    if payload ~= nil then word(payload) end
end

local function seed_record(record)
    data_space:write_u32(0x00030103, 0x00030200)
    data_space:write_u32(0x00030200, 1)
    data_space:write_u32(0x00030201, 0)
    data_space:write_u32(0x00030104, 0x00030300)
    for index, value in ipairs(record) do
        data_space:write_u32(0x000302ff + index, value)
    end
end

local function submit(test)
    command(0x17)
    word(0x00000000)
    word(test[1])
    word(test[2])
    log(string.format("probe: case=%d %s", case_index, test[3]))
end

emu.register_periodic(function()
    frame = frame + 1
    if not fifo_space then
        local maincpu = manager.machine.devices[":maincpu"]
        local copro = manager.machine.devices[":copro_adsp"]
        if maincpu and copro then
            fifo_space = maincpu.spaces[":program"] or maincpu.spaces["program"]
            data_space = copro.spaces[":data"] or copro.spaces["data"]
            log_file = assert(io.open(os.getenv("VON_SHARC_17_SENTINEL_LOG") or
                "von-sharc-opcode-17-sentinel-geometry.log", "w"))
            log("probe: start")
        end
    end
    if not fifo_space or not data_space then return end
    if frame >= 600 and (frame - 600) % 220 == 0 then
        case_index = case_index + 1
        if case_index <= #cases then
            command(0x0d, 0x00000000)
            pending = frame + 20
        end
    end
    if pending and frame == pending then
        pending = nil
        seed_record(records[case_index])
        submit(cases[case_index])
    end
    if frame >= 1600 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
