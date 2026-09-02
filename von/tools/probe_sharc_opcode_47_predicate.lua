-- Upload a zeroed 0x30150 state prefix, then probe opcode 0x47 around its
-- inferred radial and difference thresholds. Bootstrap state14/state15 are
-- 0.5 and 3.0 respectively.

local frame = 0
local space
local log_file
local cases = {
    { name = "inside-both", values = {3.0, 4.0, 6.0, 4.0} },
    { name = "radial-boundary", values = {3.0, 4.0, 5.0, 2.0} },
    { name = "below-low", values = {3.0, 4.0, 6.0, 5.75} },
    { name = "above-high", values = {3.0, 4.0, 6.0, 2.0} },
}

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

local function upload_predicate_state()
    header(0x46)
    for _, value in ipairs({
        0x00000000, -- state[0]
        0x00000000, -- state[1]
        0x40400000, -- state[2] = upper delta bound 3.0
        0x00000000, -- state[3]
        0x3f000000, -- state[4] = lower delta bound 0.5
        0x00000000, -- state[5]
        0x00000000, -- state[6]
    }) do word(value) end
end

local function run_case(case)
    header(0x47)
    for _, value in ipairs(case.values) do
        local bits = ({
            [3.0] = 0x40400000, [4.0] = 0x40800000,
            [5.0] = 0x40a00000, [6.0] = 0x40c00000,
            [2.0] = 0x40000000, [-2.0] = 0xc0000000,
            [-0.25] = 0xbe800000, [-4.0] = 0xc0800000,
        })[value]
        word(bits)
    end
    log("probe: case=" .. case.name)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_47_LOG") or
                "von-sharc-opcode-47-predicate.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then upload_predicate_state() end
    if frame == 720 then
        header(0x44)
        log("probe: initialized opcode-0x47 thresholds via opcode=0x44")
    end
    for index, case in ipairs(cases) do
        if frame == 800 + (index - 1) * 300 then run_case(case) end
    end
    if frame >= 2050 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
