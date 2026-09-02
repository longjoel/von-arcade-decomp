-- Measure opcode 0x31's combined R10/R9 rotation order.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_31_COMBINED_LOG") or
                "vonj-sharc-opcode-31-combined.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 100 then
        word(0x00000008); word(0x00000031)
        word(0x41200000); word(0x41a00000); word(0x41f00000)
        word(0x4000); word(0x4000)
        word(0x3f800000); word(0x40000000); word(0x40400000)
        log("probe: tail=(10,20,30), R10=R9=0x4000, vector=(1,2,3)")
    elseif frame >= 300 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
