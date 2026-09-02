-- Isolated SHARC opcode 0x0f probe; select vector with VON_0F_VECTOR (1..3).

local frame = 0
local injected = false
local space
local log_file
local vectors = {
    { 0x3f800000, 0x00000000, 0x00000000, 0x00000000 },
    { 0x00000000, 0x3f800000, 0x00000000, 0x00000000 },
    { 0x3f800000, 0x3f800000, 0x00000000, 0x00000000 },
    { 0x00000000, 0xbf800000, 0x00000000, 0x00000000 },
    { 0xbf800000, 0x00000000, 0x00000000, 0x00000000 },
    { 0x3f800000, 0xbf800000, 0x00000000, 0x00000000 },
    { 0x00000000, 0x00000000, 0x00000000, 0x00000000 },
}
local index = tonumber(os.getenv("VON_0F_VECTOR") or "1")

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function inject()
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000000f)
    for _, word in ipairs(vectors[index]) do
        space:write_u32(0x00884000, word)
    end
    injected = true
    log("probe: injected opcode=0x0f vector-index=" .. index)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0F_LOG") or
                "vonj-sharc-opcode-0f-single.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 1800 then inject() end
    if frame >= 2050 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
