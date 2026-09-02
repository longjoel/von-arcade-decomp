-- Serialize isolated angle packets for opcode 0x30 and trace state writes.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function packet(r15, r13)
    word(0x00000008)
    word(0x00000030)
    word(0)
    word(0)
    word(0)
    word(r15)
    word(r13)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_30_ANGLES_LOG") or
                "vonj-sharc-opcode-30-angles.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        packet(0x4000, 0)
        log("probe: R15=0x4000")
    elseif frame == 1000 then
        packet(0, 0x4000)
        log("probe: R13=0x4000")
    elseif frame >= 1400 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
