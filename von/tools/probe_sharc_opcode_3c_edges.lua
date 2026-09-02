-- Probe opcode 0x3c's edge vectors, reading back the complete state after
-- each case through opcode 0x11. Cases: XZ-degenerate, zero, and X-axis.

local frame = 0
local space
local log_file
local cases = {
    { name = "xz-degenerate-y", values = {0x00000000, 0x3f800000, 0x00000000} },
    { name = "zero", values = {0x00000000, 0x00000000, 0x00000000} },
    { name = "x-axis", values = {0x3f800000, 0x00000000, 0x00000000} },
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

local function run_case(case)
    header(0x10)
    header(0x3c)
    for _, value in ipairs(case.values) do word(value) end
    header(0x11)
    log("probe: case=" .. case.name)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_3C_EDGES_LOG") or
                "von-sharc-opcode-3c-edges.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    for index, case in ipairs(cases) do
        if frame == 600 + (index - 1) * 240 then run_case(case) end
    end
    if frame >= 1250 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
