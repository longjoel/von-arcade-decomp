-- Exercise opcode 0x23 from a fresh identity affine state for each vector.
local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end
local function word(value) space:write_u32(0x00884000, value) end
local function header(opcode) word(0x00000008); word(opcode) end

local identity = {
    0x3f800000, 0, 0, 0, 0x3f800000, 0,
    0, 0, 0x3f800000, 0, 0, 0,
}
local cases = {
    { "x-axis", 0x3f800000, 0, 0 },
    { "y-axis", 0, 0x3f800000, 0 },
    { "z-axis", 0, 0, 0x3f800000 },
    { "diagonal", 0x3f800000, 0x40000000, 0x40400000 },
}

local function send_case(case)
    header(0x07)
    for _, value in ipairs(identity) do word(value) end
    header(0x23)
    word(case[2]); word(case[3]); word(case[4])
    log("probe: case=" .. case[1])
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_23_LOG") or
                "von-sharc-opcode-23-axes.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then send_case(cases[1])
    elseif frame == 850 then send_case(cases[2])
    elseif frame == 1100 then send_case(cases[3])
    elseif frame == 1350 then send_case(cases[4])
    elseif frame >= 1650 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
