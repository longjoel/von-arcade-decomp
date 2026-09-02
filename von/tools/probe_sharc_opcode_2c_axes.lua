-- Compare all three signed-angle fields with serialized identity resets.

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

local function reset()
    header(0x10)
end

local function field(which)
    header(0x2c)
    word(0)
    word(0)
    word(0)
    word(which == 13 and 0x40 or 0)
    word(which == 14 and 0x40 or 0)
    word(which == 15 and 0x40 or 0)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_2C_AXES_LOG") or
                "vonj-sharc-opcode-2c-axes.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        reset()
        log("probe: reset before R13")
    elseif frame == 900 then
        field(13)
        log("probe: R13=0x0040")
    elseif frame == 1200 then
        header(0x11)
        log("probe: readback after R13")
    elseif frame == 1500 then
        reset()
        log("probe: reset before R15")
    elseif frame == 1800 then
        field(15)
        log("probe: R15=0x0040")
    elseif frame == 2100 then
        header(0x11)
        log("probe: readback after R15")
    elseif frame >= 2400 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
