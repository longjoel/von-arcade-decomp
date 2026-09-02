-- Exercise the real nonzero opcode-0x17 record path with a seeded SHARC
-- internal table and record.  The record is deliberately non-degenerate.

local frame = 0
local fifo_space
local data_space
local log_file

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

local function command_17_header()
    fifo_space:write_u32(0x00884000, 0x00000008)
    fifo_space:write_u32(0x00884000, 0x00000017)
    fifo_space:write_u32(0x00884000, 0x00000000)
    fifo_space:write_u32(0x00884000, 0x00000000)
    fifo_space:write_u32(0x00884000, 0x00000000)
    log("probe: command=0x17 operands=0,0,0")
end

local function seed_record()
    -- DM 0x30103 points at the selector table.  Its first word is the
    -- record count and the following word is the selected-record index.
    -- DM 0x30104 points at the 16-word record bank.
    data_space:write_u32(0x00030103, 0x00030200)
    data_space:write_u32(0x00030200, 1)
    data_space:write_u32(0x00030201, 0)
    data_space:write_u32(0x00030104, 0x00030300)

    -- Four first vertices/auxiliary values chosen to pass the ROM's
    -- nonzero determinant gate.  The exact aliased register expression is
    -- intentionally left to the instruction trace rather than guessed here.
    local record = {
        0x3f800000, 0x40000000, 0x40a00000,
        0x40800000, 0x40e00000, 0x40c00000,
        0x41100000, 0x41000000, 0x40400000,
        0x41200000, 0x41300000, 0x41400000
    }
    for index, value in ipairs(record) do
        data_space:write_u32(0x000302ff + index, value)
    end
    log("probe: seeded table=0x30200 count=1 selector=0 record_base=0x30300")
end

emu.register_periodic(function()
    frame = frame + 1
    if not fifo_space then
        local maincpu = manager.machine.devices[":maincpu"]
        local copro = manager.machine.devices[":copro_adsp"]
        if maincpu and copro then
            fifo_space = maincpu.spaces[":program"] or maincpu.spaces["program"]
            data_space = copro.spaces[":data"] or copro.spaces["data"]
            log_file = assert(io.open(os.getenv("VON_SHARC_17_NONZERO_LOG") or
                "von-sharc-opcode-17-nonzero.log", "w"))
            log("probe: start")
        end
    end
    if not fifo_space or not data_space then return end
    if frame == 600 then
        -- The dispatcher requires the one-word 0x0d packet before this
        -- service, matching the framing used by the original focused probe.
        command(0x0d, 0x00000000)
    end
    if frame == 700 then
        seed_record()
    end
    if frame == 800 then
        -- R0 selects the table base; R8/R9 are helper auxiliary words.
        command_17_header()
    end
    if frame >= 1000 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
