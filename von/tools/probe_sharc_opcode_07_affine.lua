-- Load a complete affine state through opcode 0x07, then exercise opcode 0x1a.
-- The payload is row-major 3x3 state followed by the persistent translation.

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
            log_file = assert(io.open(os.getenv("VON_SHARC_07_AFFINE_LOG") or
                "von-sharc-opcode-07-affine.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x07)
        local state = {
            0x3f800000, 0x00000000, 0x00000000,
            0x00000000, 0x3f800000, 0x00000000,
            0x00000000, 0x00000000, 0x3f800000,
            0x41200000, 0x41a00000, 0x41f00000,
        }
        for _, value in ipairs(state) do word(value) end
        log("probe: loaded 12-word affine state")
    end
    -- Keep the 14-word loader and 5-word consumer in separate FIFO bursts;
    -- the hardware input FIFO is only 16 words deep.
    if frame == 780 then
        header(0x1a)
        word(0x3f800000)
        word(0x40000000)
        word(0x40400000)
        log("probe: state=identity translation=10,20,30 vector=1,2,3")
    end
    if frame >= 900 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
