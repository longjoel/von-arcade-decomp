-- Isolate one non-axis opcode 0x25 vector to avoid FIFO interleaving.
local frame = 0
local space
local log_file
local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end
local function word(value) space:write_u32(0x00884000, value) end
local function header(opcode) word(0x00000008); word(opcode) end
emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_25_DIAGONAL_LOG") or
                "von-sharc-opcode-25-diagonal.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x07)
        for _, value in ipairs({
            0x3f800000, 0, 0, 0, 0x3f800000, 0,
            0, 0, 0x3f800000, 0, 0, 0,
        }) do word(value) end
        header(0x25)
        -- Stream order is R1,R0,R2: y=2, x=1, z=3.
        word(0x40000000); word(0x3f800000); word(0x40400000)
        log("probe: diagonal=(1,2,3)")
    elseif frame >= 1800 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
