-- Serialize opcode 0x31 angle fields R10 and R9 with a unit scalar tail.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function packet(label, r10, r9)
    word(0x00000008); word(0x00000031)
    word(0x3f800000); word(0x40000000); word(0x40400000)
    word(r10); word(r9); word(0); word(0); word(0)
    log("probe: " .. label)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_31_R9_R10_LOG") or
                "vonj-sharc-opcode-31-r9-r10.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        packet("R10=0, R9=0", 0, 0)
    elseif frame == 1000 then
        packet("R10=0x4000, R9=0", 0x4000, 0)
    elseif frame == 1400 then
        packet("R10=0, R9=0x4000", 0, 0x4000)
    elseif frame >= 1800 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
