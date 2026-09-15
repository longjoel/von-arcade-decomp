-- Watch the player's action-input bytes (object+0x138/0x139/0x13a) and the
-- selected action (object+0x174) while driving every available button, to learn
-- which inputs fire which of the three weapon actions (and whether action 3 is
-- reachable at all from the MAME `von` inputs).
--
--   VON_ACT_LOG=out.log mame vonj ... -autoboot_script \
--     von/tools/probe_action_bytes.lua

local LOG = assert(os.getenv("VON_ACT_LOG"), "VON_ACT_LOG required")
local COIN = tonumber(os.getenv("VON_ACT_COIN") or "7200")
local START = tonumber(os.getenv("VON_ACT_START") or "7400")
local BATTLE = tonumber(os.getenv("VON_ACT_BATTLE") or "9500")
local WINDOW = tonumber(os.getenv("VON_ACT_WINDOW") or "600")
local PLAYER = 0x00503ad0

-- label -> {left_shot, right_shot, left_dash, right_dash}
local PHASES = {
    { "left",   { 1, 0, 0, 0 } },
    { "right",  { 0, 1, 0, 0 } },
    { "both",   { 1, 1, 0, 0 } },
    { "ldash",  { 0, 0, 1, 0 } },
    { "rdash",  { 0, 0, 0, 1 } },
    { "lshot+ldash", { 1, 0, 1, 0 } },
    { "rshot+rdash", { 0, 1, 0, 1 } },
    { "both+dash",   { 1, 1, 1, 1 } },
}

local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "2 Players Start" },
    left_shot = { ":IN1", "P1 Left Shot" },
    left_dash = { ":IN1", "P1 Left Dash" },
    right_shot = { ":IN2", "P1 Right Shot" },
    right_dash = { ":IN2", "P1 Right Dash" },
}

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("act: session start")

local frame = 0
local space
local fields = {}

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

local function phase_for(f)
    local span = WINDOW
    local idx = math.floor((f - BATTLE) / span)
    if idx >= 0 and idx < #PHASES then return PHASES[idx + 1] end
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

    local p = phase_for(frame)
    if p then
        local label, cmd = p[1], p[2]
        local on = (frame % 24) < 4
        set_key("left_shot", on and cmd[1] == 1)
        set_key("right_shot", on and cmd[2] == 1)
        set_key("left_dash", cmd[3] == 1)
        set_key("right_dash", cmd[4] == 1)
        if frame % 30 == 0 then
            local b0 = space:read_u8(PLAYER + 0x138)
            local b1 = space:read_u8(PLAYER + 0x139)
            local b2 = space:read_u8(PLAYER + 0x13a)
            local act = space:read_u8(PLAYER + 0x174)
            local ph = space:read_u8(PLAYER + 0x176)
            log(string.format("act: f%d win=%s in=%02x/%02x/%02x action=%d phase=%d",
                frame, label, b0, b1, b2, act, ph))
        end
    end
end)
