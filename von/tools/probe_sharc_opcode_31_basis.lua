-- Recover the emitted 0x31 transform columns with mixed-angle basis vectors.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function case(label, x, y, z)
    word(0x00000008); word(0x00000031)
    word(0); word(0); word(0)
    word(0x1000); word(0x3000)
    word(x); word(y); word(z)
    log("probe: " .. label)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_31_BASIS_LOG") or
                "vonj-sharc-opcode-31-basis.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 100 then
        case("basis-x", 0x3f800000, 0, 0)
    elseif frame == 220 then
        case("basis-y", 0, 0x3f800000, 0)
    elseif frame == 340 then
        case("basis-z", 0, 0, 0x3f800000)
    elseif frame >= 460 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
