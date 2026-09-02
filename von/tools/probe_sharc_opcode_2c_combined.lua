-- Serialize one mixed-angle X/Y/Z packet and read the state back.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function header(opcode)
    word(0x00000008)
    word(opcode)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_2C_COMBINED_LOG") or
                "vonj-sharc-opcode-2c-combined.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 100 then
        header(0x10)
        log("probe: identity reset")
    elseif frame == 200 then
        header(0x2c)
        for _ = 1, 3 do word(0) end
        word(0x00001000)
        word(0x00002000)
        word(0x00003000)
        log("probe: combined R13=0x1000 R14=0x2000 R15=0x3000")
    elseif frame == 300 then
        header(0x11)
        log("probe: state readback")
    elseif frame >= 400 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
