-- Dump a range of the player object across a jump so the position/velocity
-- cells can be located by differencing.
--
--   VON_PD_LOG=out.log mame vonj ... -autoboot_script \
--     von/tools/probe_player_dump.lua

local LOG = assert(os.getenv("VON_PD_LOG"), "VON_PD_LOG required")
local COIN = tonumber(os.getenv("VON_PD_COIN") or "7200")
local START = tonumber(os.getenv("VON_PD_START") or "7400")
local PLAYER = 0x00503ad0
local BASE = tonumber(os.getenv("VON_PD_BASE") or "0")
local WORDS = tonumber(os.getenv("VON_PD_WORDS") or "0x80")  -- words (u32)

local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "2 Players Start" },
    l_left = { ":IN1", "P1 Left Stick/Left" },
    r_right = { ":IN2", "P1 Right Stick/Right" },
    l_right = { ":IN1", "P1 Left Stick/Right" },
    l_up = { ":IN1", "P1 Left Stick/Up" },
}
-- Strafe right between dumps so the x/z cells move.
local DUMP_FRAMES = { 9600, 9630, 9660, 9690, 9720, 9750 }

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("pd: session start")

local frame = 0
local space
local fields = {}
local dump_idx = 1

local function setup()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then return false end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    for key, spec in pairs(FIELDS) do
        local port = manager.machine.ioport.ports[spec[1]]
        fields[key] = port and port.fields[spec[2]] or nil
    end
    return space ~= nil and fields.coin ~= nil
end

local function set_key(key, on)
    local f = fields[key]
    if not f then return end
    if on then f:set_value(1) else f:clear_value() end
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        if frame % 60 == 1 then setup() end
        return
    end
    if not fields.coin then return end
    if frame == COIN then set_key("coin", true) end
    if frame == COIN + 8 then set_key("coin", false) end
    if frame == START then set_key("start", true) end
    if frame == START + 8 then set_key("start", false) end

    local chord = frame >= 9600 and frame < 9610
    set_key("l_left", chord)
    set_key("r_right", chord)
    -- Strafe right with the left stick (both-stick-right is the strafe input).
    set_key("l_right", frame >= 9601 and frame < 9760)
    set_key("l_up", false)

    if dump_idx <= #DUMP_FRAMES and frame == DUMP_FRAMES[dump_idx] then
        local parts = {}
        for i = 0, WORDS - 1 do
            parts[#parts + 1] = string.format("%d:%08x", BASE + i * 4,
                space:read_u32(PLAYER + BASE + i * 4))
        end
        log(string.format("pd: f%d %s", frame, table.concat(parts, " ")))
        dump_idx = dump_idx + 1
    end
end)
