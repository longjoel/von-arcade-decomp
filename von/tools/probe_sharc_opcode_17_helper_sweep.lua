-- Sweep controlled opcode-0x17 records/auxiliary inputs through the real
-- handler.  This is intended to expose the normal 0x20de1 return branch.

local frame = 0
local fifo_space
local data_space
local log_file
local case_index = 0
local pending_case
local pending_frame
local true_selector = tonumber(os.getenv("VON_SHARC_17_TRUE_SELECTOR") or "0") ~= 0

local cases = {
    { 0x00000000, 0x00000000, 1 },
    { 0x3e800000, 0x3e800000, 1 }, -- 0.25, 0.25
    { 0x3f000000, 0x3f000000, 1 }, -- 0.5, 0.5
    { 0x3f800000, 0x3f800000, 1 }, -- 1.0, 1.0
    { 0xbf800000, 0xbf800000, 1 }, -- -1.0, -1.0
    { 0x3e800000, 0x3f000000, 1 },
    { 0x3f000000, 0x3e800000, 1 },
    { 0x40000000, 0x40000000, 1 }, -- 2.0, 2.0
    { 0x00000000, 0x00000000, 2 },
    { 0x3f000000, 0x3f000000, 2 },
    { 0x00000000, 0x00000000, 3 },
    { 0x3f000000, 0x3f000000, 3 },
    { 0x3f000000, 0x00000000, 2 },
    { 0x00000000, 0x3f000000, 2 },
    { 0x3f800000, 0x00000000, 2 },
    { 0x00000000, 0x3f800000, 2 }
}

local records = {
    {
        -- Proven nondegenerate record from probe_sharc_opcode_17_nonzero.lua.
        0x3f800000, 0x40000000, 0x40a00000,
        0x40800000, 0x40e00000, 0x40c00000,
        0x41100000, 0x41000000, 0x40400000,
        0x41200000, 0x41300000, 0x41400000
    },
    {
        0x3f800000, 0x00000000, 0x3f800000,
        0x00000000, 0x00000000, 0x00000000,
        0x00000000, 0x00000000, 0x3f800000,
        0x00000000, 0x00000000, 0x00000000
    },
    {
        0x40000000, 0x40000000, 0x40a00000,
        0x40800000, 0x40e00000, 0x40c00000,
        0x41100000, 0x41000000, 0x40400000,
        0x41200000, 0x41300000, 0x41400000
    },
    {
        0x3f800000, 0x40400000, 0x40a00000,
        0x40800000, 0x41000000, 0x40c00000,
        0x41100000, 0x41100000, 0x40400000,
        0x41200000, 0x41400000, 0x41400000
    },
    {
        -- Record 1 translated by +1 in every x coordinate.
        0x40000000, 0x40000000, 0x40a00000,
        0x40a00000, 0x40e00000, 0x40c00000,
        0x41200000, 0x41000000, 0x40400000,
        0x41300000, 0x41300000, 0x41400000
    }
}

-- A fresh process can focus on one record without carrying the selector/state
-- pointer through the long exploratory sweep.  Set VON_SHARC_17_SINGLE_RECORD
-- to 1, 2, or 3 to run origin, x-axis, y-axis, and diagonal probes only.
local single_record = tonumber(os.getenv("VON_SHARC_17_SINGLE_RECORD") or "0")
if single_record >= 1 and single_record <= #records then
    cases = {
        { 0x00000000, 0x00000000, single_record },
        { 0x3f800000, 0x00000000, single_record },
        { 0x00000000, 0x3f800000, single_record },
        { 0x3f000000, 0x3f000000, single_record },
    }
    local single_point = tonumber(os.getenv("VON_SHARC_17_SINGLE_POINT") or "0")
    if single_point >= 1 and single_point <= #cases then
        cases = { cases[single_point] }
    end
end

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function command(opcode, payload)
    fifo_space:write_u32(0x00884000, 0x00000008)
    fifo_space:write_u32(0x00884000, opcode)
    if payload ~= nil then fifo_space:write_u32(0x00884000, payload) end
    log(string.format("probe: command=0x%02x payload=%08x", opcode,
        payload or 0))
end

local function write_17(aux0, aux1)
    fifo_space:write_u32(0x00884000, 0x00000008)
    fifo_space:write_u32(0x00884000, 0x00000017)
    fifo_space:write_u32(0x00884000, 0x00000000)
    fifo_space:write_u32(0x00884000, aux0)
    fifo_space:write_u32(0x00884000, aux1)
    log(string.format("probe: case=%d aux=%08x,%08x record=%d",
        case_index, aux0, aux1, cases[case_index][3]))
end

local function seed(record, selector)
    data_space:write_u32(0x00030103, 0x00030200)
    data_space:write_u32(0x00030200, 1)
    data_space:write_u32(0x00030201, selector or 0)
    data_space:write_u32(0x00030104, 0x00030300)
    if true_selector then
        -- The ROM shifts the selected table value left by four before
        -- MODIFY(I5, M7), so selector values address 16-word bank slots.
        -- Populate all slots to make selector experiments independent of
        -- stale words left by an earlier packet.
        for bank, bank_record in ipairs(records) do
            for index, value in ipairs(bank_record) do
                data_space:write_u32(0x00030300 + (bank - 1) * 16 + index - 1,
                    value)
            end
        end
    else
        for index, value in ipairs(record) do
            data_space:write_u32(0x000302ff + index, value)
        end
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
            log_file = assert(io.open(os.getenv("VON_SHARC_17_SWEEP_LOG") or
                "von-sharc-opcode-17-helper-sweep.log", "w"))
            log("probe: start")
        end
    end
    if not fifo_space or not data_space then return end
    if frame >= 700 and (frame - 700) % 150 == 0 then
        case_index = case_index + 1
        if case_index <= #cases then
            -- Opcode 0x0d consumes exactly one payload word and refreshes
            -- the selector/record base pointers.  It is asynchronous, so
            -- seed and queue 0x17 only after a short processing delay.
            command(0x0d, 0x00000000)
            pending_case = case_index
            pending_frame = frame + (true_selector and 60 or 10)
        end
    end
    if pending_case and frame == pending_frame then
        local test = cases[pending_case]
        pending_case = nil
        pending_frame = nil
        seed(records[test[3]], true_selector and (test[3] - 1) or 0)
        write_17(test[1], test[2])
    end
    if (single_record > 0 and frame >= 1400) or
        (single_record == 0 and frame >= 3200) then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
