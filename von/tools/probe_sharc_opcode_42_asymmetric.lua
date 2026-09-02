-- Seed an asymmetric matrix, then exercise opcode 0x42 with three quarter turns.

local frame = 0
local space
local log_file

local function word(value) space:write_u32(0x00884000, value) end
local function header(opcode) word(0x00000008); word(opcode) end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_42_ASYMMETRIC_LOG") or
                "vonj-sharc-opcode-42-asymmetric.log", "w"))
            log_file:write("probe: start\n")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x07)
        for _, value in ipairs({
            0x3f800000, 0x40000000, 0x40400000,
            0x40800000, 0x40a00000, 0x40c00000,
            0x40e00000, 0x41000000, 0x41100000,
            0, 0, 0,
        }) do word(value) end
        log_file:write("probe: seeded matrix=1..9\n"); log_file:flush()
    elseif frame == 780 then
        header(0x42)
        for _, value in ipairs({0, 0, 0, 0x4000, 0x4000, 0x4000}) do word(value) end
        log_file:write("probe: angles=0x4000,0x4000,0x4000\n"); log_file:flush()
    end
    if frame >= 1100 then
        log_file:write("probe: complete\n"); log_file:close(); manager.machine:exit()
    end
end)
