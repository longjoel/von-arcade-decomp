-- Log per-frame player position while holding/releasing the sticks, to recover
-- the horizontal acceleration/deceleration profile (the movement "cadence").
--
-- Player x/z = object+0x08/+0x10. Both sticks forward = walk +Z at the round
-- start (facing +Z); both sticks right = strafe +X.
--
--   VON_MOVE_LOG=out.log mame vonj ... -autoboot_script \
--     von/tools/probe_move_cadence.lua

local LOG = assert(os.getenv("VON_MOVE_LOG"), "VON_MOVE_LOG required")
local COIN = tonumber(os.getenv("VON_MOVE_COIN") or "7200")
local START = tonumber(os.getenv("VON_MOVE_START") or "7400")
local PLAYER = 0x00503ad0

local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "2 Players Start" },
    l_up = { ":IN1", "P1 Left Stick/Up" },
    r_up = { ":IN2", "P1 Right Stick/Up" },
    l_down = { ":IN1", "P1 Left Stick/Down" },
    r_down = { ":IN2", "P1 Right Stick/Down" },
    l_right = { ":IN1", "P1 Left Stick/Right" },
    r_right = { ":IN2", "P1 Right Stick/Right" },
}

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("move: session start")

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

-- (from, to, label, forward, strafe, back). Short holds so the +-320 wall is
-- never reached (player starts at z=-60).
local PHASES = {
    { 9600, 9660, "fwd", 1, 0, 0 },
    { 9660, 9760, "fwd_rel", 0, 0, 0 },
    { 9800, 9860, "back", 0, 0, 1 },
    { 9860, 9960, "back_rel", 0, 0, 0 },
    { 10000, 10060, "strafe", 0, 1, 0 },
    { 10060, 10160, "strafe_rel", 0, 0, 0 },
}

local function phase_for(f)
    for _, p in ipairs(PHASES) do
        if f >= p[1] and f < p[2] then return p end
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

    local p = phase_for(frame)
    local fwd = p ~= nil and p[4] == 1
    local strafe = p ~= nil and p[5] == 1
    local back = p ~= nil and p[6] == 1
    set_key("l_up", fwd)
    set_key("r_up", fwd)
    set_key("l_down", back)
    set_key("r_down", back)
    set_key("l_right", strafe)
    set_key("r_right", strafe)

    if frame >= 9595 and frame <= 10170 then
        log(string.format("move: f%d x=0x%08x z=0x%08x label=%s",
            frame, space:read_u32(PLAYER + 0x08), space:read_u32(PLAYER + 0x10),
            p and p[3] or "-"))
    end
end)
