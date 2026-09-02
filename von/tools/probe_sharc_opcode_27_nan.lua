-- Probe unordered weighted-magnitude comparison in SHARC opcode 0x27.

local frame = 0
local space
local log_file

local function word(value) space:write_u32(0x00884000, value) end

local function opcode27(x, z)
    word(0x00000008); word(0x00000027)
    word(x); word(0); word(z)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_27_NAN_LOG") or
                "vonj-sharc-opcode-27-nan.log", "w"))
            log_file:write("probe: start\n"); log_file:flush()
        end
    end
    if not space then return end
    if frame == 600 then
        word(0x00000008); word(0x00000026)
        for _, value in ipairs({0x3f800000, 0, 0x3f800000, 0x41200000, 0}) do word(value) end
        opcode27(0x7fc00000, 0)
        log_file:write("probe: case=nan-input\n"); log_file:flush()
    elseif frame == 760 then
        word(0x00000008); word(0x00000026)
        for _, value in ipairs({0x3f800000, 0, 0x3f800000, 0x7fc00000, 0}) do word(value) end
        opcode27(0, 0)
        log_file:write("probe: case=nan-threshold\n"); log_file:flush()
    elseif frame >= 920 then
        log_file:write("probe: complete\n"); log_file:close()
        manager.machine:exit()
    end
end)
