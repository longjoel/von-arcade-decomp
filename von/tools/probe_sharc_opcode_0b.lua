-- Directly exercise SHARC opcode 0x0b (eight-input vector service).

local TARGET_FRAMES = 2100
local INJECT_FRAME = 1800
local frame = 0
local space
local injection_count = 0
local log_file

local function log(message)
    if log_file then
        log_file:write(message .. "\n")
        log_file:flush()
    end
end

local function inject()
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000000b)
    -- First six words are two endpoint triples; the final two exercise the
    -- additional pair consumed by the second difference path.
    local words = {
        0x40400000, 0x40800000, 0x41400000,
        0x00000000, 0x00000000, 0x00000000,
        0x3f800000, 0x3f800000,
    }
    for _, word in ipairs(words) do
        space:write_u32(0x00884000, word)
    end
    injection_count = injection_count + 1
    log("probe: injected opcode=0x0b vector-index=" .. injection_count)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0B_LOG") or
                "vonj-sharc-opcode-0b-probe.log", "w"))
            log("probe: start")
        end
    end
    if not space then
        return
    end
    if frame == INJECT_FRAME then
        inject()
    end
    if frame >= TARGET_FRAMES then
        log("probe: complete")
        if log_file then
            log_file:close()
        end
        manager.machine:exit()
    end
end)
