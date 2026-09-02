-- Exercise opcode 0x2e packed parameters, then read back persistent state.

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

local function case(label, values)
    header(0x10)
    header(0x2e)
    for _, value in ipairs(values) do word(value) end
    header(0x11)
    log("probe: " .. label)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_2E_LOG") or
                "vonj-sharc-opcode-2e-packed.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        case("neutral", {0, 0, 0, 0, 0, 0})
    end
    if frame == 800 then
        case("packed-R0-half-1", {0x00003c00, 0, 0, 0, 0, 0})
    end
    if frame == 1000 then
        case("packed-R0-half-2", {0x00004000, 0, 0, 0, 0, 0})
    end
    if frame == 1200 then
        case("signed-low-byte-R13-0x40", {0, 0, 0, 0x40, 0, 0})
    end
    if frame >= 1400 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
