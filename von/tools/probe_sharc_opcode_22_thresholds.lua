-- Isolate opcode 0x22's four clip thresholds and depth fallback.
local frame = 0
local space
local log_file
local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end
local function word(value) space:write_u32(0x00884000, value) end
local function header(opcode) word(0x00000008); word(opcode) end
local identity = { 0x3f800000, 0, 0, 0, 0x3f800000, 0, 0, 0, 0x3f800000, 0, 0, 0 }
local wide = { 0x3f800000, 0x3f800000, 0x42c80000, 0xc2c80000, 0x42c80000, 0xc2c80000 }
local cases = {
    { "baseline", wide, 0x3f800000, 0x40000000, 0x40400000 },
    { "flip-s2", { 0x3f800000, 0x3f800000, 0xc2c80000, 0xc2c80000, 0x42c80000, 0xc2c80000 }, 0x3f800000, 0x40000000, 0x40400000 },
    { "flip-s3", { 0x3f800000, 0x3f800000, 0x42c80000, 0x42c80000, 0x42c80000, 0xc2c80000 }, 0x3f800000, 0x40000000, 0x40400000 },
    { "flip-s4", { 0x3f800000, 0x3f800000, 0x42c80000, 0xc2c80000, 0xc2c80000, 0xc2c80000 }, 0x3f800000, 0x40000000, 0x40400000 },
    { "flip-s5", { 0x3f800000, 0x3f800000, 0x42c80000, 0xc2c80000, 0x42c80000, 0x42c80000 }, 0x3f800000, 0x40000000, 0x40400000 },
    { "negative-depth", wide, 0x3f800000, 0x40000000, 0xc0400000 },
}
local function send_case(case)
    header(0x07)
    for _, value in ipairs(identity) do word(value) end
    header(0x21)
    for _, value in ipairs(case[2]) do word(value) end
    header(0x22)
    word(case[3]); word(case[4]); word(case[5]); word(0)
    log("probe: case=" .. case[1])
end
emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_22_THRESHOLDS_LOG") or
                "von-sharc-opcode-22-thresholds.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    local index = math.floor((frame - 600) / 240) + 1
    if frame >= 600 and frame <= 600 + (#cases - 1) * 240 and (frame - 600) % 240 == 0 then
        send_case(cases[index])
    elseif frame >= 2200 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
