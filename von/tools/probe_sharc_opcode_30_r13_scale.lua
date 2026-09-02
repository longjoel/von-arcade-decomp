-- Probe opcode 0x30 with a floating-point R13 scale and optional R15 angle.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function packet(label, r15, r13)
    word(0x00000008); word(0x00000030)
    word(0); word(0); word(0); word(r15); word(r13)
    log("probe: " .. label)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_30_R13_LOG") or
                "vonj-sharc-opcode-30-r13-scale.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        packet("R15=0, R13=1.0", 0, 0x3f800000)
    elseif frame == 1000 then
        packet("R15=quarter-turn, R13=1.0", 0x4000, 0x3f800000)
    elseif frame >= 1400 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
