-- Probe opcode 0x45 with two signed-16 angles and a non-unit scale.

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
            log_file = assert(io.open(os.getenv("VON_SHARC_45_LOG") or
                "vonj-sharc-opcode-45-trig.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        word(0x00000008); word(0x00000045)
        word(0x00002000) -- +pi/4 fixed-point angle
        word(0x00004000) -- +pi/2 fixed-point angle
        word(0x40000000) -- scale = 2.0
        log("probe: angles=(0x4000,0x2000), scale=2.0")
    end
    if frame >= 1100 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
