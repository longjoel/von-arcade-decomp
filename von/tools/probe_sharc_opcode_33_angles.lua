-- Isolate opcode 0x33's two signed-16 matrix fields.

local frame = 0
local space
local log_file

local function word(value) space:write_u32(0x00884000, value) end
local function case(label, r14, r13)
    word(0x00000008); word(0x00000010)
    word(0x00000008); word(0x00000033)
    word(0); word(0); word(0); word(r14); word(r13)
    word(0x00000008); word(0x00000011)
    log_file:write("probe: " .. label .. "\n"); log_file:flush()
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_33_ANGLES_LOG") or
                "vonj-sharc-opcode-33-angles.log", "w"))
            log_file:write("probe: start\n")
        end
    end
    if not space then return end
    if frame == 600 then case("R14-signed-0x4000", 0x4000, 0) end
    if frame == 800 then case("R13-signed-0x4000", 0, 0x4000) end
    if frame >= 1000 then
        log_file:write("probe: complete\n"); log_file:close(); manager.machine:exit()
    end
end)
