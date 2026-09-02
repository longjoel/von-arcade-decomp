-- Contrast probe for the helper 0x20de1 equality-tail sentinel path.

local frame = 0
local fifo_space
local data_space
local log_file
local pending

local record = {
    0x3f800000, 0x40000000, 0x40a00000,
    0x40800000, 0x40e00000, 0x40c00000,
    0x41100000, 0x41000000, 0x40400000,
    0x41200000, 0x41300000, 0x41400000,
}

local record2 = {
    0x40000000, 0x40000000, 0x40a00000,
    0x40800000, 0x40e00000, 0x40c00000,
    0x41100000, 0x41000000, 0x40400000,
    0x41200000, 0x41300000, 0x41400000,
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

local function seed_record()
    data_space:write_u32(0x00030103, 0x00030200)
    data_space:write_u32(0x00030200, 2)
    data_space:write_u32(0x00030201, 0)
    data_space:write_u32(0x00030202, 1)
    data_space:write_u32(0x00030104, 0x00030300)
    for index, value in ipairs(record) do
        data_space:write_u32(0x000302ff + index, value)
    end
    for index, value in ipairs(record2) do
        data_space:write_u32(0x0003030f + index, value)
    end
end

emu.register_periodic(function()
    frame = frame + 1
    if not fifo_space then
        local maincpu = manager.machine.devices[":maincpu"]
        local copro = manager.machine.devices[":copro_adsp"]
        if maincpu and copro then
            fifo_space = maincpu.spaces[":program"] or maincpu.spaces["program"]
            data_space = copro.spaces[":data"] or copro.spaces["data"]
            log_file = assert(io.open(os.getenv("VON_SHARC_17_CONTRAST_LOG") or
                "von-sharc-opcode-17-prevalidation-contrast.log", "w"))
            log("probe: contrast record normal fixture, query=(0,0)")
        end
    end
    if fifo_space and data_space and frame == 600 then
        command(0x0d, 0x00000000)
        pending = frame + 20
    elseif pending and frame == pending then
        pending = nil
        seed_record()
        command(0x17)
        word(0x00000000)
        word(0x00000000)
        word(0x00000000)
    end
    if frame >= 1100 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
