-- Probe opcode 0x3e's four-input scalar result with two 2D difference pairs.
local frame = 0
local space
local log_file
local cases = {
    {name = "zero-difference", values = {0, 0, 0, 0}},
    {name = "nan-input", values = {0x7fc00000, 0, 0, 0}},
}
local selected = tonumber(os.getenv("VON_SHARC_3E_EDGE") or "1")
local function log(s) if log_file then log_file:write(s .. "\n"); log_file:flush() end end
local function word(v) space:write_u32(0x00884000, v) end
local function send(case)
    word(0x00000008); word(0x0000003e)
    for _, v in ipairs(case.values) do word(v) end
    log("probe: case=" .. case.name)
end
emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_3E_LOG") or
                "von-sharc-opcode-3e-distance.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    for index, case in ipairs(cases) do
        if frame == 600 and index == selected then send(case) end
    end
    if frame >= 1100 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
