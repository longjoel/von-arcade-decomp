-- Install a known diagonal matrix, then exercise opcode 0x38 with packed
-- coordinates (1, 2, 3).  The MAME output trace captures the three results.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function header(opcode)
    word(0x00000008)
    word(opcode)
    log(string.format("probe: header=0x%02x", opcode))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_38_MATRIX_LOG") or
                "von-sharc-opcode-38-matrix.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x10)
        header(0x13)
        word(0x40000000)
        word(0x40400000)
        word(0x40800000)
        header(0x38)
        word(0x00003c00)
        word(0x00004000)
        word(0x00004200)
        log("probe: matrix-scale=2,3,4 packed-vector=1,2,3")
    end
    if frame >= 900 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
