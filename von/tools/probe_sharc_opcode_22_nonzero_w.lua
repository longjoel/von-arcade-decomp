-- Validate opcode 0x22 perspective-plane expressions with nonzero w.
local frame = 0
local space
local log_file
local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end
local function word(value) space:write_u32(0x00884000, value) end
local function header(opcode) word(0x00000008); word(opcode) end
local function send()
    header(0x07)
    for _, value in ipairs({
        0x3f800000, 0, 0, 0, 0x3f800000, 0,
        0, 0, 0x3f800000, 0, 0, 0,
    }) do word(value) end
    header(0x21)
    -- p=2, q=3; all thresholds are wide.
    for _, value in ipairs({
        0x40000000, 0x40400000, 0x42c80000,
        0xc2c80000, 0x42c80000, 0xc2c80000,
    }) do word(value) end
    header(0x22)
    -- (x,y,z,w) = (1,2,3,1), stream order is direct R0..R3.
    word(0x3f800000); word(0x40000000); word(0x40400000); word(0x3f800000)
    log("probe: nonzero-w (1,2,3,1), p=2, q=3")
end
emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_22_NONZERO_W_LOG") or
                "von-sharc-opcode-22-nonzero-w.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then send()
    elseif frame >= 1000 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
