-- Isolate opcode 0x34's direct translation fields with neutral signed fields.

local frame = 0
local space
local log_file

local function word(value) space:write_u32(0x00884000, value) end
local function header(opcode)
    word(0x00000008)
    word(opcode)
end

local function case(label, values)
    header(0x10)
    header(0x34)
    for _, value in ipairs(values) do word(value) end
    header(0x11)
    log_file:write("probe: " .. label .. "\n")
    log_file:flush()
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_34_LOG") or
                "vonj-sharc-opcode-34-float.log", "w"))
            log_file:write("probe: start\n")
        end
    end
    if not space then return end
    if frame == 600 then
        case("direct-float=(1,2,3), signed-fields=(0,0,0,0,0)",
            {0x3f800000, 0x40000000, 0x40400000, 0, 0, 0, 0, 0})
    end
    if frame >= 900 then
        log_file:write("probe: complete\n")
        log_file:close()
        manager.machine:exit()
    end
end)
