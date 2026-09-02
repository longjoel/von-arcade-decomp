-- Serialize combined low-byte X/Y/Z quarter turns for opcode 0x2e.

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
            log_file = assert(io.open(os.getenv("VON_SHARC_2E_COMBINED_LOG") or
                "vonj-sharc-opcode-2e-combined.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 100 then
        header(0x10)
        header(0x2e)
        word(0); word(0); word(0)
        word(0x40); word(0x40); word(0x40)
        header(0x11)
        log("probe: combined low-byte R13=R14=R15=0x40")
    elseif frame >= 300 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
