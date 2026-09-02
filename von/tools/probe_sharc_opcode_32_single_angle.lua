-- Serialize one opcode-0x32 signed angle field for direct state tracing.

local frame = 0
local space
local log_file
local field = os.getenv("VON_SHARC_32_FIELD") or "R3"

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
            log_file = assert(io.open(os.getenv("VON_SHARC_32_SINGLE_LOG") or
                "vonj-sharc-opcode-32-single-angle.log", "w"))
            log("probe: start field=" .. field)
        end
    end
    if not space then return end
    if frame == 600 then
        local r3, r5, r6 = 0, 0, 0
        if field == "R3" then r3 = 0x4000 end
        if field == "R5" then r5 = 0x4000 end
        if field == "R6" then r6 = 0x4000 end
        word(0x00000008); word(0x00000010)
        word(0x00000008); word(0x00000032)
        word(0); word(0); word(0); word(r3)
        word(0); word(0); word(0); word(r5); word(r6)
        log("probe: " .. field .. "=0x4000, all other fields zero")
    elseif frame >= 1000 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
