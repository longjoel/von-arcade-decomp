-- Serialize one opcode-0x33 signed field after an identity reset.

local frame = 0
local space
local log_file
local field = os.getenv("VON_SHARC_33_FIELD") or "R14"

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
            log_file = assert(io.open(os.getenv("VON_SHARC_33_SINGLE_LOG") or
                "vonj-sharc-opcode-33-single-angle.log", "w"))
            log("probe: start field=" .. field)
        end
    end
    if not space then return end
    if frame == 600 then
        local r14, r13 = 0, 0
        if field == "R14" then r14 = 0x4000 end
        if field == "R13" then r13 = 0x4000 end
        word(0x00000008); word(0x00000010)
        word(0x00000008); word(0x00000033)
        word(0x3f800000); word(0x40000000); word(0x40400000)
        word(r14); word(r13)
        log("probe: " .. field .. "=0x4000, tail=(1,2,3)")
    elseif frame >= 1000 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
