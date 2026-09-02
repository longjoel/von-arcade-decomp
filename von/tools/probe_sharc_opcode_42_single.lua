-- Isolate one opcode 0x42 packed-coordinate/angle input and read state.

local frame = 0
local space
local log_file
local field = os.getenv("VON_SHARC_42_FIELD") or "neutral"
local values = {
    neutral = {0, 0, 0, 0, 0, 0},
    R0 = {0x3c00, 0, 0, 0, 0, 0},
    R1 = {0, 0x3c00, 0, 0, 0, 0},
    R2 = {0, 0, 0x3c00, 0, 0, 0},
    R13 = {0, 0, 0, 0x4000, 0, 0},
    R14 = {0, 0, 0, 0, 0x4000, 0},
    R15 = {0, 0, 0, 0, 0, 0x4000},
}

local function word(value) space:write_u32(0x00884000, value) end
local function header(opcode) word(0x00000008); word(opcode) end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_42_LOG") or
                "vonj-sharc-opcode-42-single.log", "w"))
            log_file:write("probe: start field=" .. field .. "\n")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x10); header(0x42)
        for _, value in ipairs(values[field] or values.neutral) do word(value) end
        header(0x11)
        log_file:write("probe: field=" .. field .. "\n"); log_file:flush()
    end
    if frame >= 1000 then
        log_file:write("probe: complete\n"); log_file:close(); manager.machine:exit()
    end
end)
