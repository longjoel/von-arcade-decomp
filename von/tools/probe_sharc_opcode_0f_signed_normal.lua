-- Short isolated probe for the signed normal path of helper 0x20d68.
-- The default vector forms (x,y)=(1,-1) in opcode 0x0f's difference lanes.

local frame = 0
local injected = false
local space
local log_file
local vector = {
    0x3f800000, 0xbf800000, 0x00000000, 0x00000000,
}

local function word(value) space:write_u32(0x00884000, value) end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_0F_SIGNED_LOG") or
                "von-sharc-opcode-0f-signed-normal.log", "w"))
            log_file:write("probe: start vector=(1,-1)\n")
        end
    end
    if not space then return end
    if frame == 600 and not injected then
        word(0x00000008); word(0x0000000f)
        for _, value in ipairs(vector) do word(value) end
        injected = true
        log_file:write("probe: injected\n"); log_file:flush()
    elseif frame >= 900 then
        log_file:write("probe: complete\n")
        log_file:close()
        manager.machine:exit()
    end
end)
