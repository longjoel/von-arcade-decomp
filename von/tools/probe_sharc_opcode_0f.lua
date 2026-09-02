-- Directly exercise SHARC opcode 0x0f (two-component reduction).

local TARGET_FRAMES = 2250
local INJECT_FRAME = 1800
local frame = 0
local space
local injection_count = 0
local log_file

local vectors = {
    { 0x3f800000, 0x00000000, 0x00000000, 0x00000000 }, -- (x,y)=(0,1)
    { 0x00000000, 0x3f800000, 0x00000000, 0x00000000 }, -- (x,y)=(1,0)
    { 0x3f800000, 0x3f800000, 0x00000000, 0x00000000 }, -- diagonal
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function inject()
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000000f)
    for _, word in ipairs(vectors[injection_count + 1]) do
        space:write_u32(0x00884000, word)
    end
    injection_count = injection_count + 1
    log("probe: injected opcode=0x0f vector-index=" .. injection_count)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0F_LOG") or
                "vonj-sharc-opcode-0f-probe.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame >= INJECT_FRAME and (frame - INJECT_FRAME) % 120 == 0 and
        injection_count < #vectors then inject() end
    if frame >= TARGET_FRAMES then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
