-- Directly exercise SHARC opcode 0x0d (one-word state-base setup).

local TARGET_FRAMES = 2400
local INJECT_FRAME = 1800
local frame = 0
local space
local injected = 0
local log_file

local function log(message)
    if log_file then
        log_file:write(message .. "\n")
        log_file:flush()
    end
end

local inputs = { 0x00000000, 0x00000001, 0x00000002, 0x00000010 }

local function inject(value, index)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000000d)
    space:write_u32(0x00884000, value)
    injected = index
    log(string.format("probe: injected opcode=0x0d input=0x%08x index=%d", value, index))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0D_LOG") or
                "vonj-sharc-opcode-0d-probe.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame >= INJECT_FRAME and (frame - INJECT_FRAME) % 140 == 0 then
        local index = math.floor((frame - INJECT_FRAME) / 140) + 1
        if inputs[index] then inject(inputs[index], index) end
    end
    if frame >= TARGET_FRAMES then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
