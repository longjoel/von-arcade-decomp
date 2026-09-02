-- Isolate one of opcode 0x31's direct R13/R14/R15 matrix-pass fields.

local frame = 0
local space
local log_file
local field = os.getenv("VON_SHARC_31_DIRECT_FIELD") or "R13"

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
            log_file = assert(io.open(os.getenv("VON_SHARC_31_DIRECT_LOG") or
                "vonj-sharc-opcode-31-direct-fields.log", "w"))
            log("probe: start field=" .. field)
        end
    end
    if not space then return end
    if frame == 600 then
        local r13, r14, r15 = 0, 0, 0
        if field == "R13" then r13 = 0x3f800000 end
        if field == "R14" then r14 = 0x3f800000 end
        if field == "R15" then r15 = 0x3f800000 end
        word(0x00000008); word(0x00000031)
        word(0x3f800000); word(0x40000000); word(0x40400000)
        word(0); word(0); word(r13); word(r14); word(r15)
        log("probe: " .. field .. "=1.0, R9/R10=0")
    elseif frame >= 1000 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
