-- Compare candidate bit placements for one packed 0x2e rotation field.

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

local function case(label, r13)
    header(0x10)
    header(0x2e)
    word(0); word(0); word(0)
    word(r13); word(0); word(0)
    header(0x11)
    log(string.format("probe: %s r13=0x%08x", label, r13))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_2E_ANGLE_LOG") or
                "vonj-sharc-opcode-2e-angle-encoding.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 100 then
        case("low-byte", 0x00000040)
    elseif frame == 220 then
        case("low-halfword", 0x00004000)
    elseif frame == 340 then
        case("high-byte", 0x40000000)
    elseif frame >= 460 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
