-- Directly exercise SHARC opcode 0x0c (three-input vector normalization).

local TARGET_FRAMES = 2250
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
    -- The dispatcher consumes the service marker, then the raw table opcode.
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000000c)
    local words
    if injection_count == 0 then
        words = { 0x40400000, 0x40800000, 0x41400000 }
    else
        words = { 0x00000000, 0x00000000, 0x00000000 }
    end
    for _, word in ipairs(words) do
        space:write_u32(0x00884000, word)
    end
    injection_count = injection_count + 1
    log("probe: injected opcode=0x0c vector-index=" .. injection_count)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0C_LOG") or
                "vonj-sharc-opcode-0c-probe.log", "w"))
            log("probe: start")
        end
    end
    if not space then
        return
    end
    if frame >= INJECT_FRAME and (frame - INJECT_FRAME) % 120 == 0 and
        injection_count < 2 then
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
