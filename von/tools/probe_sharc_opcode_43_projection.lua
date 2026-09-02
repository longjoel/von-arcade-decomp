-- Load an asymmetric matrix through opcode 0x07 and project a vector with 0x43.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then
        log_file:write(message .. "\n")
        log_file:flush()
    end
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
            log_file = assert(io.open(os.getenv("VON_SHARC_43_LOG") or
                "vonj-sharc-opcode-43-projection.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x07)
        for _, value in ipairs({
            0x3f800000, 0x40000000, 0x40400000,
            0x40800000, 0x40a00000, 0x40c00000,
            0x40e00000, 0x41000000, 0x41100000,
            0x41200000, 0x41300000, 0x41400000,
        }) do word(value) end
        header(0x43)
        word(0x41200000)
        word(0x41a00000)
        word(0x41f00000)
        log("probe: matrix=1..9 vector=(10,20,30)")
    end
    if frame >= 1200 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
