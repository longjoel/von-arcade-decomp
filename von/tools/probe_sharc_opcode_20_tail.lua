-- Load a known affine state through opcode 0x07, then read its translation
-- tail through opcode 0x20. The packets are split because the FIFO is 16 words.

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
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_20_TAIL_LOG") or
                "von-sharc-opcode-20-tail.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x07)
        local state = {
            0x3f800000, 0, 0,
            0, 0x3f800000, 0,
            0, 0, 0x3f800000,
            0x41200000, 0x41a00000, 0x41f00000,
        }
        for _, value in ipairs(state) do word(value) end
        log("probe: loaded identity plus tail 10,20,30")
    end
    if frame == 780 then
        header(0x20)
        log("probe: requested opcode=0x20 tail readback")
    end
    if frame >= 960 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
