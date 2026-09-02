-- Probe unordered comparison behavior in SHARC opcode 0x28.

local frame = 0
local space
local log_file

local function word(value)
    space:write_u32(0x00884000, value)
end

local function request(values)
    word(0x00000008); word(0x00000028)
    for _, value in ipairs(values) do word(value) end
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_28_NAN_LOG") or
                "vonj-sharc-opcode-28-nan.log", "w"))
            log_file:write("probe: start\n"); log_file:flush()
        end
    end
    if not space then return end
    if frame == 600 then
        word(0x00000008); word(0x00000010)
        request({0x7fc00000, 0x00000000, 0x3f800000, 0x40000000, 0x40000000})
        log_file:write("probe: case=nan-x\n"); log_file:flush()
    elseif frame == 760 then
        request({0x00000000, 0x00000000, 0x7fc00000, 0x40000000, 0x40000000})
        log_file:write("probe: case=nan-depth\n"); log_file:flush()
    elseif frame >= 940 then
        log_file:write("probe: complete\n"); log_file:close()
        manager.machine:exit()
    end
end)
