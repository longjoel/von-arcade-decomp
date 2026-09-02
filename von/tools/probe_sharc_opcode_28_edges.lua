-- Probe finite and singular edges of SHARC opcode 0x28.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function request(values)
    word(0x00000008)
    word(0x00000028)
    for _, value in ipairs(values) do word(value) end
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_28_EDGE_LOG") or
                "vonj-sharc-opcode-28-edges.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end

    if frame == 600 then
        -- Select the normal state window and install identity through opcode 0x10.
        word(0x00000008); word(0x00000010)
        log("probe: initialized identity state")
    elseif frame == 760 then
        request({0x00000000, 0x00000000, 0x3f800000, 0x40000000, 0x40000000})
        log("probe: case=unit-z")
    elseif frame == 900 then
        request({0x00000000, 0x00000000, 0x00000000, 0x40000000, 0x40000000})
        log("probe: case=zero-horizontal")
    elseif frame == 1040 then
        request({0x00000000, 0x00000000, 0xbf800000, 0x40000000, 0x40000000})
        log("probe: case=negative-depth")
    elseif frame >= 1240 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
