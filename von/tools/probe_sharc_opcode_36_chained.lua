-- Validate opcode 0x36 tail addition against a nonzero prior tail.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function header(opcode)
    word(0x00000008)
    word(opcode)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_36_CHAINED_LOG") or
                "vonj-sharc-opcode-36-chained.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 100 then
        header(0x10); header(0x37)
        word(0x41200000); word(0x41a00000); word(0x41f00000)
        log("probe: seeded tail=(10,20,30)")
    elseif frame == 220 then
        header(0x36)
        word(0x3f800000); word(0x40000000); word(0x40400000)
        header(0x11)
        log("probe: add=(1,2,3), scale=2")
    elseif frame >= 400 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
