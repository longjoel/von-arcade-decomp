-- Single-case opcode 0x47 probe.  State2=3.0 and state4=0.5 are the
-- comparison bounds; state0/state1/state3/state5/state6 are zero.
local frame = 0
local space
local log_file
local function word(v) space:write_u32(0x00884000, v) end
local function header(op) word(0x00000008); word(op) end
local function send_case()
    header(0x46)
    for _, v in ipairs({0x00000000, 0x00000000, 0x00000000, 0x40400000,
                        0x3f000000, 0x00000000, 0x00000000}) do word(v) end
    header(0x44)
    header(0x47)
    for _, v in ipairs({0x40400000, 0x40800000, 0x40c00000, 0xc0000000}) do word(v) end
    if log_file then log_file:write("probe: interior case (3,4,4,-2)\n"); log_file:flush() end
end
emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_47_SINGLE_LOG") or
                "von-sharc-opcode-47-single.log", "w"))
        end
    end
    if not space then return end
    if frame == 600 then send_case() end
    if frame >= 1500 then
        if log_file then log_file:write("probe: complete\n"); log_file:close() end
        manager.machine:exit()
    end
end)
