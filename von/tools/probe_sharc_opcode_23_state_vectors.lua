-- Probe opcode 0x23 state writes with non-identity affine seeds.
local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end
local function word(value) space:write_u32(0x00884000, value) end
local function header(opcode) word(0x00000008); word(opcode) end

local zero = 0
local seed_a = {
    0x3f800000, 0x40000000, 0x40400000,
    0x40800000, 0x40a00000, 0x40c00000,
    0x40e00000, 0x41000000, 0x41100000,
    zero, zero, zero,
}
local seed_b = {
    0x3f000000, 0xbf000000, 0x3fc00000,
    0xc0000000, 0x40200000, 0xc0400000,
    0x40600000, 0xc0800000, 0x40a00000,
    zero, zero, zero,
}
local cases = {
    { "seed-a-x", seed_a, 0x3f800000, 0, 0 },
    { "seed-a-z", seed_a, 0, 0, 0x3f800000 },
    { "seed-b-x", seed_b, 0x3f800000, 0, 0 },
    { "seed-b-z", seed_b, 0, 0, 0x3f800000 },
}

local function send_case(case)
    header(0x07)
    for _, value in ipairs(case[2]) do word(value) end
    header(0x23)
    word(case[3]); word(case[4]); word(case[5])
    log("probe: case=" .. case[1])
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_23_STATE_LOG") or
                "von-sharc-opcode-23-state-vectors.log", "w"))
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
