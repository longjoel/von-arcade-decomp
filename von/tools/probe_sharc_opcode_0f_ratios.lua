-- Exercise opcode 0x0f with several finite ratios for helper 0x20d68 tracing.

local frame = 0
local index = 0
local space
local log_file
local vectors = {
    { 0x40000000, 0x3f800000, 0x00000000, 0x00000000 }, -- helper (1,2)
    { 0x3f800000, 0x40000000, 0x00000000, 0x00000000 }, -- helper (2,1)
    { 0xc0000000, 0x3f800000, 0x00000000, 0x00000000 }, -- helper (1,-2)
    { 0x3f800000, 0xc0000000, 0x00000000, 0x00000000 }, -- helper (-2,1)
    { 0x40800000, 0x3f800000, 0x00000000, 0x00000000 }, -- helper (1,4)
    { 0x3f800000, 0x40800000, 0x00000000, 0x00000000 }, -- helper (4,1)
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function inject(vector)
    space:write_u32(0x00884000, 0x00000008)
    space:write_u32(0x00884000, 0x0000000f)
    for _, word in ipairs(vector) do space:write_u32(0x00884000, word) end
    index = index + 1
    log("probe: injected ratio-index=" .. index)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_0F_LOG") or
                "vonj-sharc-opcode-0f-ratios.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame >= 1800 and (frame - 1800) % 120 == 0 and index < #vectors then
        inject(vectors[index + 1])
    end
    if frame >= 2600 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
