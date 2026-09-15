-- Read the player's ordnance records while firing one weapon per window, to
-- find the byte that identifies the weapon (the damage-table index).
--
-- The hit applier reads table[type*16] with type = byte 0 of the projectile
-- record (i960 0xbe0f0), so dumping the raw record at spawn shows the type
-- directly, without needing a connect. Player mech = 0x503ad0.
--
--   VON_OID_LOG=out.log mame vonj ... -autoboot_script \
--     von/tools/probe_ordnance_id.lua

local LOG = assert(os.getenv("VON_OID_LOG"), "VON_OID_LOG required")
local COIN = tonumber(os.getenv("VON_OID_COIN") or "7200")
local START = tonumber(os.getenv("VON_OID_START") or "7400")
local BATTLE = tonumber(os.getenv("VON_OID_BATTLE") or "9500")
local WINDOW = tonumber(os.getenv("VON_OID_WINDOW") or "1500")
local PLAYER = 0x00503ad0

local WINDOWS = {
    { "left",   BATTLE + 100, BATTLE + 100 + WINDOW },
    { "right",  BATTLE + 100 + WINDOW, BATTLE + 100 + 2 * WINDOW },
    { "center", BATTLE + 100 + 2 * WINDOW, BATTLE + 100 + 3 * WINDOW },
}

local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "2 Players Start" },
    left_shot = { ":IN1", "P1 Left Shot" },
    right_shot = { ":IN2", "P1 Right Shot" },
}

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("oid: session start")

local frame = 0
local space
local fields = {}
local last_active_by_slot = {}

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

local function window_for(f)
    for _, w in ipairs(WINDOWS) do
        if f >= w[2] and f < w[3] then return w[1] end
    end
    return nil
end

local function scan(tag)
    for i = 0, 31 do
        local base = PLAYER + 0x200 + i * 0x20
        local b0 = space:read_u8(base)
        if b0 ~= 0 then
            local bytes = {}
            for k = 0, 15 do
                bytes[#bytes + 1] = string.format("%02x", space:read_u8(base + k))
            end
            log(string.format("oid: f%d win=%s slot=%d bytes=%s",
                frame, tag, i, table.concat(bytes, " ")))
            last_active_by_slot[i] = tag
        end
    end
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
        local on = (frame % 24) < 3
        set_key("left_shot", on and (win == "left" or win == "center"))
        set_key("right_shot", on and (win == "right" or win == "center"))
        if frame % 6 == 0 then scan(win) end
    end
end)
