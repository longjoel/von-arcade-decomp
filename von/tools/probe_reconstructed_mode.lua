-- Observe the reconstructed image's root mode/phase and attract state.
--
--   VON_MODE_LOG=out.log ./bin/vonctl i960 reconstructed \
--     -video none -sound none -skip_gameinfo -seconds_to_run 20 \
--     -autoboot_script von/tools/probe_reconstructed_mode.lua

local LOG_PATH = os.getenv("VON_MODE_LOG") or "von-reconstructed-mode.log"
local GAME_MODE = 0x005039f4
local MODE_PHASE = 0x00503a00
local WORKRAM = 0x00500000

local file = assert(io.open(LOG_PATH, "w"))
local frame = 0
local space

local function setup()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then
        return false
    end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    return space ~= nil
end

local function r32(address)
    local ok, value = pcall(function() return space:read_u32(address) end)
    return ok and value or 0xffffffff
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        if frame % 60 == 1 then
            setup()
        end
        return
    end
    local state = WORKRAM + 0x20
    file:write(string.format(
        "frame=%d mode=%d phase=%08x heartbeat=%08x tag=%08x attr=%08x geom=%08x\n",
        frame, r32(GAME_MODE), r32(MODE_PHASE), r32(state + 5 * 4),
        r32(state + 4 * 4), r32(state + 9 * 4), r32(state + 10 * 4)))
    if frame % 30 == 0 then
        file:flush()
    end
end)
