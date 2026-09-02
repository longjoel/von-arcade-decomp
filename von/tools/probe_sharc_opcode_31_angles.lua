-- Isolate opcode 0x31's two signed-16 parameter fields.

local frame = 0
local space
local log_file

local function word(value)
    space:write_u32(0x00884000, value)
end

local function case(label, values)
    word(0x00000008); word(0x00000031)
    for _, value in ipairs(values) do word(value) end
    log_file:write("probe: " .. label .. "\n")
    log_file:flush()
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_31_ANGLES_LOG") or
                "vonj-sharc-opcode-31-angles.log", "w"))
            log_file:write("probe: start\n")
        end
    end
    if not space then return end
    local tail = {0x3f800000, 0x40000000, 0x40400000}
    if frame == 600 then
        case("baseline", {tail[1], tail[2], tail[3], 0, 0, 0, 0, 0})
    end
    if frame == 800 then
        case("R10-signed-0x4000", {tail[1], tail[2], tail[3], 0x4000, 0, 0, 0, 0})
    end
    if frame == 1000 then
        case("R9-signed-0x4000", {tail[1], tail[2], tail[3], 0, 0x4000, 0, 0, 0})
    end
    if frame >= 1200 then
        log_file:write("probe: complete\n")
        log_file:close()
        manager.machine:exit()
    end
end)
