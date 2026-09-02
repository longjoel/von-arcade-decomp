-- Isolate opcode 0x30's direct-float R13 field against R15 rotation.

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

local function case(label, r15, r13)
    header(0x10)
    header(0x30)
    word(0); word(0); word(0); word(r15); word(r13)
    header(0x11)
    log(string.format("probe: %s r15=0x%08x r13=0x%08x", label, r15, r13))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_30_SCALAR_LOG") or
                "vonj-sharc-opcode-30-scalar-readback.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 100 then
        case("neutral-half", 0, 0x3f000000)
    elseif frame == 220 then
        case("neutral-one", 0, 0x3f800000)
    elseif frame == 340 then
        case("neutral-two", 0, 0x40000000)
    elseif frame == 460 then
        case("quarter-half", 0x4000, 0x3f000000)
    elseif frame == 580 then
        case("quarter-two", 0x4000, 0x40000000)
    elseif frame >= 740 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
