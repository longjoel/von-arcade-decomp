-- Isolate opcode 0x31's second signed angle (R9).

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
            log_file = assert(io.open(os.getenv("VON_SHARC_31_R9_LOG") or
                "vonj-sharc-opcode-31-r9-single.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        word(0x00000008); word(0x00000031)
        word(0x3f800000); word(0x40000000); word(0x40400000)
        word(0); word(0x4000); word(0); word(0); word(0)
        log("probe: R9=0x4000")
    elseif frame >= 1000 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
