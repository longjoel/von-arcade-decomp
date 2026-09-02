-- Exercise opcode 0x22 with identity affine state and clip bounds.
local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end
local function word(value) space:write_u32(0x00884000, value) end
local function header(opcode) word(0x00000008); word(opcode) end

local cases = {
    { "inside",  0x3f800000, 0x40000000, 0x40400000, 0x00000000 },
    { "outside", 0x41200000, 0x40000000, 0x40400000, 0x00000000 },
    { "negative",0xc1200000, 0x40000000, 0x40400000, 0x00000000 },
}

local function send_case(case)
    header(0x22)
    for index = 2, #case do word(case[index]) end
    log("probe: case=" .. case[1])
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_22_LOG") or
                "von-sharc-opcode-22-edges.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x07)
        for _, value in ipairs({
            0x3f800000, 0, 0, 0,
            0x3f800000, 0, 0, 0, 0x3f800000,
            0, 0, 0,
        }) do word(value) end
        log("probe: loaded identity affine state")
    elseif frame == 780 then
        header(0x21)
        -- Coefficients are one for the identity-style test.  The four
        -- thresholds follow the handler's alternating upper/lower tests:
        -- +100, -100, +100, -100 lets ordinary finite projections through.
        for _, value in ipairs({
            0x3f800000, 0x3f800000, 0x42c80000,
            0xc2c80000, 0x42c80000, 0xc2c80000,
        }) do word(value) end
        log("probe: loaded wide alternating clip parameters")
    elseif frame == 960 then
        send_case(cases[1])
    elseif frame == 1140 then
        send_case(cases[2])
    elseif frame == 1320 then
        send_case(cases[3])
    elseif frame >= 1600 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
