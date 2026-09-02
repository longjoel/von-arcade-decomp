-- Probe opcode 0x4d with zero and NaN horizontal seeds.

local frame = 0
local space
local log_file

local cases = {
    { name = "zero-seed", vector = {0, 0x40800000, 0, 0} },
    { name = "nan-seed", vector = {0x7fc00001, 0x40800000, 0, 0x3f800000} },
}

local function word(value)
    space:write_u32(0x00884000, value)
end

local function header(opcode)
    word(0x00000008); word(opcode)
end

local function initialize()
    header(0x48)
    for _, value in ipairs({0, 0, 0, 0x40800000, 0x40a00000}) do word(value) end
    header(0x44)
end

local function run_case(case)
    header(0x4d)
    for _, value in ipairs(case.vector) do word(value) end
    log_file:write("probe: case=" .. case.name .. "\n")
    log_file:flush()
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_4D_EDGE_LOG") or
                "vonj-sharc-opcode-4d-edge.log", "w"))
            log_file:write("probe: start\n")
        end
    end
    if not space then return end
    if frame == 600 then initialize() end
    if frame == 840 then run_case(cases[1]) end
    if frame == 1000 then run_case(cases[2]) end
    if frame >= 1250 then
        log_file:write("probe: complete\n")
        log_file:close()
        manager.machine:exit()
    end
end)
