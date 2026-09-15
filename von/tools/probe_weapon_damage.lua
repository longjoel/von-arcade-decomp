-- Measure per-weapon applied damage from the opponent's working-health cell.
--
-- Fire one weapon per window (left tap, right tap, center = held left+right)
-- and log the opponent's working health (0x5042a0) and display (0x5042a2), the
-- player's working health (0x503ca0), and the current damage-table type.
-- Drops in 0x5042a0 partition by window give the applied damage per weapon.
--
--   VON_DMG_LOG=out.log mame vonj ... -autoboot_script \
--     von/tools/probe_weapon_damage.lua

local LOG = assert(os.getenv("VON_DMG_LOG"), "VON_DMG_LOG required")
local COIN = tonumber(os.getenv("VON_DMG_COIN") or "7200")
local START = tonumber(os.getenv("VON_DMG_START") or "7400")
local BATTLE = tonumber(os.getenv("VON_DMG_BATTLE") or "9500")
local WINDOW = tonumber(os.getenv("VON_DMG_WINDOW") or "1200")

local WINDOWS = {
    { "left",   BATTLE + 100, BATTLE + 100 + WINDOW },
    { "right",  BATTLE + 100 + WINDOW, BATTLE + 100 + 2 * WINDOW },
    { "center", BATTLE + 100 + 2 * WINDOW, BATTLE + 100 + 3 * WINDOW },
    { "none",   BATTLE + 100 + 3 * WINDOW, BATTLE + 100 + 4 * WINDOW },
}

local TABLE_BASE = 0x00565ed0
local TABLE_LEN = 0x334 * 4
local OPP_WORK = 0x005042a0
local OPP_DISP = 0x005042a2
local PL_WORK = 0x00503ca0

local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "2 Players Start" },
    left_shot = { ":IN1", "P1 Left Shot" },
    right_shot = { ":IN2", "P1 Right Shot" },
}

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("dmg: session start")

local frame = 0
local space
local cpu
local fields = {}
local reading = false
local last_type = -1

local function setup()
    cpu = manager.machine.devices[":maincpu"]
    if not cpu then return false end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    for key, spec in pairs(FIELDS) do
        local port = manager.machine.ioport.ports[spec[1]]
        fields[key] = port and port.fields[spec[2]] or nil
    end
    if not space then return false end
    space:install_read_tap(TABLE_BASE, TABLE_BASE + TABLE_LEN - 1, "dmgtype",
        function(address, data, mask)
            if reading then return end
            reading = true
            last_type = math.floor((address - TABLE_BASE) / 16)
            reading = false
            return data
        end)
    return true
end

local function set_key(key, on)
    local f = fields[key]
    if not f then return end
    if on then f:set_value(1) else f:clear_value() end
end

local function window_for(f)
    for _, w in ipairs(WINDOWS) do
        if f >= w[2] and f < w[3] then return w[1] end
    end
    return nil
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

    local win = window_for(frame)
    if win then
        if win == "center" then
            set_key("left_shot", true)
            set_key("right_shot", true)
        else
            local on = (frame % 24) < 3
            set_key("left_shot", on and win == "left")
            set_key("right_shot", on and win == "right")
        end
    end

    if frame >= BATTLE and frame % 2 == 0 then
        local ow = space:read_u16(OPP_WORK)
        local od = space:read_u16(OPP_DISP)
        local pw = space:read_u16(PL_WORK)
        log(string.format("dmg: f%d win=%s pw=%d ow=%d od=%d type=%d",
            frame, win or "wait", pw, ow, od, last_type))
        last_type = -1
    end
end)
