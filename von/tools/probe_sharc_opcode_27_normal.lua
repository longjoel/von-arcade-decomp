-- Upload opcode 0x27's retained scale/state words, then probe its normal path.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function inject()
    -- opcode 0x26 retains R0/R2 as unit X/Z scales and stores state[0..3].
    word(0x00000008); word(0x00000026)
    for _, value in ipairs({0x3f800000, 0, 0x3f800000, 0x41200000, 0}) do word(value) end
    word(0x00000008); word(0x00000027)
    for _, value in ipairs({0, 0, 0}) do word(value) end
    log("probe: case=unit-scales-zero-vector-threshold10")
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_27_LOG") or
                "vonj-sharc-opcode-27-normal.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then inject() end
    if frame >= 1200 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
