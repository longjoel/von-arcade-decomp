-- Isolate opcode 0x32's first four direct floating-point fields.

local frame = 0
local space
local log_file

local function word(value) space:write_u32(0x00884000, value) end
local function header(opcode) word(0x00000008); word(opcode) end
local function case(label, values)
    header(0x10); header(0x32)
    for _, value in ipairs(values) do word(value) end
    header(0x11)
    log_file:write("probe: " .. label .. "\n"); log_file:flush()
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_32_FIELDS_LOG") or
                "vonj-sharc-opcode-32-fields.log", "w"))
            log_file:write("probe: start\n")
        end
    end
    if not space then return end
    if frame == 600 then case("R0=1", {0x3f800000,0,0,0,0,0,0,0,0}) end
    if frame == 800 then case("R1=1", {0,0x3f800000,0,0,0,0,0,0,0}) end
    if frame == 1000 then case("R2=1", {0,0,0x3f800000,0,0,0,0,0,0}) end
    if frame == 1200 then case("R3=1", {0,0,0,0x3f800000,0,0,0,0,0}) end
    if frame >= 1400 then
        log_file:write("probe: complete\n"); log_file:close(); manager.machine:exit()
    end
end)
