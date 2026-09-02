-- Probe opcode 0x3f with varied four-word inputs.

local frame = 0
local space
local log_file
local cases = {
    { name = "1,2,3,4", values = {0x3f800000, 0x40000000, 0x40400000, 0x40800000} },
    { name = "2,4,3,5", values = {0x40000000, 0x40800000, 0x40400000, 0x40a00000} },
    { name = "3,2,4,1", values = {0x40400000, 0x40000000, 0x40800000, 0x3f800000} },
    { name = "8,2,0.5,7", values = {0x41000000, 0x40000000, 0x3f000000, 0x40e00000} },
}

local function log(message)
    if log_file then
        log_file:write(message .. "\n")
        log_file:flush()
    end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function inject(case)
    word(0x00000008)
    word(0x0000003f)
    for _, value in ipairs(case.values) do word(value) end
    log("probe: case=" .. case.name)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_3F_LOG") or
                "vonj-sharc-opcode-3f-followup.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    for index, case in ipairs(cases) do
        if frame == 600 + (index - 1) * 500 then inject(case) end
    end
    if frame >= 2800 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
