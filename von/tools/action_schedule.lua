-- Deterministic twin-stick action schedule for labelling clips AND probing the
-- lock/tracking state.
--
-- Both sticks matter: from_sticks() derives move from the stick sum and twist
-- from the Y difference, so a true forward walk needs IN1-up + IN2-up (a single
-- stick is a translate+turn curve).  Reaches the match, then holds one action
-- at a time and writes an `action` line per window with the emulated time.
--
-- Optional lock trace (VON_LOCK_LOG) reads the player mech object's tracking
-- flags and the mode word every frame:
--   0x503ad0 +0xa0/+0xa1  player turret-tracking flag (parametric-aim)
--   0x5040d0 +0xa0/+0xa1  opponent
--   0x503c28              player heading (float degrees)
--   0x503a98              VS mode word (tracking cleared in mode 6)
--
-- Env: VON_ACTION_LOG (required), VON_ACTION_SECONDS (default 40),
--      VON_ACTION_START_FRAME (default 2120), VON_ACTION_CYCLES (default 2),
--      VON_LOCK_LOG (optional).

local LOG_PATH = assert(os.getenv("VON_ACTION_LOG"), "VON_ACTION_LOG required")
local LOCK_PATH = os.getenv("VON_LOCK_LOG")
local SECONDS = tonumber(os.getenv("VON_ACTION_SECONDS") or "40")
local START_FRAME = tonumber(os.getenv("VON_ACTION_START_FRAME") or "2120")
local CYCLES = tonumber(os.getenv("VON_ACTION_CYCLES") or "2")
local COIN_FRAME = tonumber(os.getenv("VON_PROGRESS_COIN_FRAME") or "900")
local MATCH_START = tonumber(os.getenv("VON_PROGRESS_START_FRAME") or "1500")

local log_file = assert(io.open(LOG_PATH, "w"))
log_file:write("action: session start\n")
log_file:flush()
local lock_file = LOCK_PATH and assert(io.open(LOCK_PATH, "w")) or nil
if lock_file then lock_file:write("lock: session start\n") lock_file:flush() end

local FIELD_NAMES = {
    coin       = { ":IN0", "Coin 1" },
    start      = { ":IN0", "1 Player Start" },
    down       = { ":IN1", "P1 Left Stick/Down" },
    up         = { ":IN1", "P1 Left Stick/Up" },
    right      = { ":IN1", "P1 Left Stick/Right" },
    left       = { ":IN1", "P1 Left Stick/Left" },
    left_shot  = { ":IN1", "P1 Left Shot" },
    left_dash  = { ":IN1", "P1 Left Dash" },
    down2      = { ":IN2", "P1 Right Stick/Down" },
    up2        = { ":IN2", "P1 Right Stick/Up" },
    right2     = { ":IN2", "P1 Right Stick/Right" },
    left2      = { ":IN2", "P1 Right Stick/Left" },
    right_shot = { ":IN2", "P1 Right Shot" },
    right_dash = { ":IN2", "P1 Right Dash" },
}

-- One action per window with idle gaps. Keys are held together.
local CYCLE = {
    { "idle", 60, {} },
    { "forward", 120, { "up", "up2" } },
    { "idle", 30, {} },
    { "back", 90, { "down", "down2" } },
    { "idle", 30, {} },
    { "strafe_left", 90, { "left", "left2" } },
    { "idle", 30, {} },
    { "strafe_right", 90, { "right", "right2" } },
    { "idle", 30, {} },
    { "turn_right", 90, { "up", "down2" } },
    { "idle", 30, {} },
    { "turn_left", 90, { "down", "up2" } },
    { "idle", 30, {} },
    { "dash_forward", 45, { "up", "up2", "left_dash" } },
    { "idle", 30, {} },
    { "guard", 60, { "right", "left2" } },
    { "idle", 30, {} },
    { "jump", 60, { "left", "right2" } },
    { "idle", 30, {} },
    { "shot_left", 60, { "left_shot" } },
    { "idle", 30, {} },
    { "shot_right", 60, { "right_shot" } },
}

local frame = 0
local space
local fields = {}
local schedule_active = false
local schedule_pos = 1
local window_end = 0
local current = "boot"
local cycles_done = 0

local function log(msg)
    log_file:write(msg .. "\n")
    log_file:flush()
end

local function now()
    local ok, t = pcall(function() return manager.machine.time:as_double() end)
    if ok and type(t) == "number" then return t end
    return frame / 60.0
end

local function setup()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then return false end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    if not space then return false end
    for key, spec in pairs(FIELD_NAMES) do
        local port = manager.machine.ioport.ports[spec[1]]
        fields[key] = port and port.fields[spec[2]] or nil
    end
    for _, key in ipairs({ "coin", "start", "up", "up2" }) do
        if not fields[key] then
            log("action: missing field " .. key)
            return false
        end
    end
    log("action: fields resolved")
    return true
end

local function set_key(key, on)
    local f = fields[key]
    if not f then return end
    if on then f:set_value(1) else f:clear_value() end
end

local function release_all()
    for key in pairs(FIELD_NAMES) do set_key(key, false) end
end

local function read_u16(addr)
    local ok, v = pcall(function() return space:read_u16(addr) end)
    if ok then return v end
    return 0
end

local function read_u32(addr)
    local ok, v = pcall(function() return space:read_u32(addr) end)
    if ok then return v end
    return 0
end

local function log_lock()
    if not lock_file then return end
    -- Player/enemy positions and heading (recovered-camera.md), the turret
    -- tracking flag, the VS mode, and the published animation header pair +
    -- frame cursor (motion-emitter selector).
    local px = read_u32(0x00503ad8)
    local pz = read_u32(0x00503ae0)
    local ex = read_u32(0x005040d8)
    local ez = read_u32(0x005040e0)
    local head = read_u32(0x00503c28)
    local pa0 = read_u16(0x00503b70)
    local mode = read_u32(0x00503a98)
    local body = read_u32(0x0051ab08)
    local paired = read_u32(0x0051ab0c)
    local cursor = read_u16(0x0051ab10)
    lock_file:write(string.format(
        "lock: t=%.6f frame=%d action=%s mode=%08x px=%08x pz=%08x ex=%08x ez=%08x head=%08x pa0=%04x body=%08x paired=%08x cur=%04x\n",
        now(), frame, current, mode, px or 0, pz or 0, ex or 0, ez or 0,
        head or 0, pa0 or 0, body or 0, paired or 0, cursor or 0))
    lock_file:flush()
end

local function open_window()
    local entry = CYCLE[schedule_pos]
    local name, frames, keys = entry[1], entry[2], entry[3]
    release_all()
    for _, k in ipairs(keys) do set_key(k, true) end
    current = name
    window_end = frame + frames
    log(string.format("action: t=%.6f frame=%d action=%s begin", now(), frame, name))
    schedule_pos = schedule_pos + 1
    if schedule_pos > #CYCLE then
        schedule_pos = 1
        cycles_done = cycles_done + 1
    end
end

local function boot_step()
    if frame < START_FRAME then
        set_key("coin", frame == COIN_FRAME)
        set_key("start", frame == MATCH_START)
        return false
    end
    if frame == START_FRAME then
        release_all()
        log(string.format("action: t=%.6f frame=%d action=match begin", now(), frame))
        schedule_active = true
        window_end = 0
    end
    return true
end

local function schedule_step()
    if not boot_step() then return end
    if not schedule_active then return end
    if frame >= window_end then
        if current ~= "boot" and current ~= "match" then
            log(string.format("action: t=%.6f frame=%d action=%s end", now(), frame, current))
        end
        if cycles_done >= CYCLES then
            release_all()
            log(string.format("action: t=%.6f frame=%d action=done", now(), frame))
            schedule_active = false
            return
        end
        open_window()
    end
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        if frame % 60 == 1 then setup() end
        return
    end
    if not fields.coin then return end
    schedule_step()
    if lock_file and schedule_active then log_lock() end
end)
