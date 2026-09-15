-- Map weapon -> damage-table projectile type by firing one weapon per window.
--
-- The hit applier (i960 0xbe0f0/0xbe170) reads table[type*16] from the runtime
-- damage table at 0x565ed0; tapping that read yields the projectile's type byte
-- (the index). Firing a single weapon per window and tagging every read with the
-- active window makes the weapon->type mapping direct. The arcade exposes left
-- and right triggers only, so the center weapon is the both-triggers window.
--
--   VON_WTYPE_LOG=out.log mame vonj ... -autoboot_script \
--     von/tools/probe_weapon_damage_type.lua

local LOG = assert(os.getenv("VON_WTYPE_LOG"), "VON_WTYPE_LOG required")
local COIN = tonumber(os.getenv("VON_WTYPE_COIN") or "7200")
local START = tonumber(os.getenv("VON_WTYPE_START") or "7400")
local BATTLE = tonumber(os.getenv("VON_WTYPE_BATTLE") or "9500")
local WINDOW = tonumber(os.getenv("VON_WTYPE_WINDOW") or "1200")

-- (weapon label, hold-window [from,to)); fired in order after BATTLE.
local WINDOWS = {
    { "left",   BATTLE + 100, BATTLE + 100 + WINDOW },
    { "right",  BATTLE + 100 + WINDOW, BATTLE + 100 + 2 * WINDOW },
    { "center", BATTLE + 100 + 2 * WINDOW, BATTLE + 100 + 3 * WINDOW },
    { "none",   BATTLE + 100 + 3 * WINDOW, BATTLE + 100 + 4 * WINDOW },
}

local TABLE_BASE = 0x00565ed0
local TABLE_LEN = 0x334 * 4
local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "2 Players Start" },
    left_shot = { ":IN1", "P1 Left Shot" },
    right_shot = { ":IN2", "P1 Right Shot" },
}

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("wtype: session start")

local frame = 0
local space
local cpu
local fields = {}
local tap
local reading = false
local active = "boot"

local function setup()
    cpu = manager.machine.devices[":maincpu"]
    if not cpu then return false end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    for key, spec in pairs(FIELDS) do
        local port = manager.machine.ioport.ports[spec[1]]
        fields[key] = port and port.fields[spec[2]] or nil
    end
    if not space then return false end
    tap = space:install_read_tap(TABLE_BASE, TABLE_BASE + TABLE_LEN - 1, "dmgtype",
        function(address, data, mask)
            if reading then return end
            reading = true
            local function st(name)
                local e = cpu.state[name]
                return e and tonumber(e.value) or -1
            end
            local off = address - TABLE_BASE
            local ty = math.floor(off / 16)
            log(string.format(
                "wtype: f%d win=%s type=%d(0x%02x) addr=%08x val=%08x g1=%08x g2=%08x g0=%08x pc=%08x",
                frame, active, ty, ty, address, data, st("g1"), st("g2"), st("g0"), st("CURPC")))
            reading = false
            return data
        end)
    return tap ~= nil
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
        active = win
        -- Tap every 24 frames (3 on / 21 off) so the edge registers.
        local on = (frame % 24) < 3
        set_key("left_shot", on and (win == "left" or win == "center"))
        set_key("right_shot", on and (win == "right" or win == "center"))
    elseif frame >= BATTLE then
        active = "wait"
    end
end)
