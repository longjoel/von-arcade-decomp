-- Probe opcode 0x25 across signed and quadrant boundary vectors.
local frame = 0
local space
local log_file
local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end
local function word(value) space:write_u32(0x00884000, value) end
local function header(opcode) word(0x00000008); word(opcode) end
local identity = { 0x3f800000, 0, 0, 0, 0x3f800000, 0, 0, 0, 0x3f800000, 0, 0, 0 }
local cases = {
    { "x-plus-z-plus", 0x3f800000, 0, 0x3f800000 },
    { "x-minus-z-plus", 0xbf800000, 0, 0x3f800000 },
    { "x-plus-z-minus", 0x3f800000, 0, 0xbf800000 },
    { "x-minus-z-minus", 0xbf800000, 0, 0xbf800000 },
    { "y-plus", 0, 0x3f800000, 0 },
    { "y-minus", 0, 0xbf800000, 0 },
    { "y-plus-z-plus", 0, 0x3f800000, 0x3f800000 },
    { "y-minus-z-plus", 0, 0xbf800000, 0x3f800000 },
}
local function send_case(case)
    header(0x07)
    for _, value in ipairs(identity) do word(value) end
    header(0x25)
    -- Stream order is R1,R0,R2: y, x, z.
    word(case[3]); word(case[2]); word(case[4])
    log("probe: case=" .. case[1])
end
emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_25_SIGNED_LOG") or
                "von-sharc-opcode-25-signed.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    local index = math.floor((frame - 550) / 200) + 1
    if frame >= 550 and frame <= 550 + (#cases - 1) * 200 and (frame - 550) % 200 == 0 then
        send_case(cases[index])
    elseif frame >= 2250 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
