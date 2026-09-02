-- Vary the six operands emitted by the i960 result-builder after command 31.
-- Each packet is command 31 plus R5/R6/R7/R10/R9/R13 host-style operands.

local frame = 0
local space
local log_file
local vectors = {
    {0x3f800000, 0x40000000, 0x40400000, 0, 0, 0, "baseline"},
    {0, 0, 0, 0, 0, 0, "zero-tail"},
    {0x3f800000, 0x40000000, 0x40400000, 0x4000, 0, 0, "r10-angle"},
    {0x3f800000, 0x40000000, 0x40400000, 0, 0x4000, 0, "r9-angle"},
    {0x3f800000, 0x40000000, 0x40400000, 0, 0, 0x3f800000, "r13-field"},
}

local function word(value)
    space:write_u32(0x00884000, value)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_31_SIX_VECTORS_LOG") or
                "vonj-sharc-opcode-31-six-vectors.log", "w"))
            log_file:write("probe: start\n")
        end
    end
    if not space then return end
    local index = math.floor((frame - 600) / 200) + 1
    if frame >= 600 and frame < 1600 and (frame - 600) % 200 == 0 then
        local v = vectors[index]
        word(0x00000008); word(0x00000031)
        for i = 1, 6 do word(v[i]) end
        log_file:write("probe: vector=" .. v[7] .. "\n")
        log_file:flush()
    elseif frame >= 1800 then
        log_file:write("probe: complete\n")
        log_file:close()
        manager.machine:exit()
    end
end)
