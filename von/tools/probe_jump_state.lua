-- Log the player's vertical/action state across jumps to recover the jump
-- state machine (cancel-vs-commit, apex behavior, hover, in-air re-jump) and
-- whether tracking/lock (object+0xa0) engages at the apex.
--
-- Jump is the outward twin-stick flick: left stick LEFT (IN1 0x80) + right
-- stick RIGHT (IN2 0x40) held together (recovered-twin-stick-map.md). Player
-- object = 0x503ad0; y = 0x503adc; tracking flag = object+0xa0.
--
--   VON_JUMP_LOG=out.log mame vonj ... -autoboot_script \
--     von/tools/probe_jump_state.lua

local LOG = assert(os.getenv("VON_JUMP_LOG"), "VON_JUMP_LOG required")
local COIN = tonumber(os.getenv("VON_JUMP_COIN") or "7200")
local START = tonumber(os.getenv("VON_JUMP_START") or "7400")
local PLAYER = 0x00503ad0

local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "2 Players Start" },
    l_left = { ":IN1", "P1 Left Stick/Left" },
    r_right = { ":IN2", "P1 Right Stick/Right" },
    l_dash = { ":IN1", "P1 Left Dash" },
    l_shot = { ":IN1", "P1 Left Shot" },
}

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("jump: session start")

local frame = 0
local space
local fields = {}
local names_logged = false

local function setup()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then return false end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    for key, spec in pairs(FIELDS) do
        local port = manager.machine.ioport.ports[spec[1]]
        fields[key] = port and port.fields[spec[2]] or nil
    end
    if not names_logged then
        local in1 = manager.machine.ioport.ports[":IN1"]
        if in1 then
            for name, _ in pairs(in1.fields) do log("jump: field " .. name) end
        end
        names_logged = true
    end
    return space ~= nil and fields.coin ~= nil
end

local function set_key(key, on)
    local f = fields[key]
    if not f then return end
    if on then f:set_value(1) else f:clear_value() end
end

-- (from, to, action) windows. chord = jump flick; tests the state machine.
local PHASES = {
    { 9600, 9610, "chord" },      -- jump 1
    { 9650, 9660, "chord" },      -- in-air re-flick mid-ascent
    { 9900, 9910, "chord" },      -- jump 2
    { 9952, 9962, "chord" },      -- in-air re-flick ~apex (apex ~9958)
    { 10200, 10210, "chord" },    -- jump 3
    { 10220, 10230, "chord" },    -- in-air re-flick very early
    { 10500, 10680, "chord" },    -- hold the chord through apex + landing (hover?)
}

local function phase_for(f)
    for _, p in ipairs(PHASES) do
        if f >= p[1] and f < p[2] then return p[3] end
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
    local chord = (p == "chord")
    local dash = (p == "dash")
    local shot = (p == "shot")
    set_key("l_left", chord)
    set_key("r_right", chord)
    set_key("l_dash", dash)
    set_key("l_shot", shot)

    if frame >= 9550 and frame <= 11020 then
        -- Position floats: x=+0x08, y=+0x0c, z=+0x10; velocity y=+0x150.
        local x = space:read_u32(PLAYER + 0x08)
        local y = space:read_u32(PLAYER + 0x0c)
        local z = space:read_u32(PLAYER + 0x10)
        local vy = space:read_u32(PLAYER + 0x150)
        local yaw = space:read_u32(PLAYER + 0x158)
        local ox = space:read_u32(0x005040d0 + 0x08)
        local oz = space:read_u32(0x005040d0 + 0x10)
        local act = space:read_u8(PLAYER + 0x174)
        local track = space:read_u8(PLAYER + 0xa0)
        log(string.format("jump: f%d in=%s x=0x%08x y=0x%08x z=0x%08x vy=0x%08x yaw=0x%08x ox=0x%08x oz=0x%08x act=%d track=%d",
            frame, p or "-", x, y, z, vy, yaw, ox, oz, act, track))
    end
end)
