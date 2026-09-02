-- Isolate opcode 0x32's final three FIFO fields R13/R14/R15.

local frame = 0
local space
local log_file

local function word(value) space:write_u32(0x00884000, value) end
local function header(opcode) word(0x00000008); word(opcode) end
local function case(label, values)
    header(0x10); header(0x32)
    for _, value in ipairs(values) do word(value) end
    log_file:write("probe: " .. label .. "\n"); log_file:flush()
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_32_RETAINED_LOG") or
                "vonj-sharc-opcode-32-retained.log", "w"))
            log_file:write("probe: start\n")
        end
    end
    if not space then return end
    if frame == 600 then
        case("R13=1", {0, 0, 0, 0, 0, 0, 0x3f800000, 0, 0})
    elseif frame == 800 then
        case("R14=1", {0, 0, 0, 0, 0, 0x3f800000, 0, 0, 0})
    elseif frame == 1000 then
        case("R15=1", {0, 0, 0, 0, 0x3f800000, 0, 0, 0, 0})
    elseif frame >= 1200 then
        log_file:write("probe: complete\n"); log_file:close(); manager.machine:exit()
    end
end)
