-- Hold a controlled arcade match while the ROM opponent attacks. This is a
-- capture experiment for genuine hit and recovery selector transitions.
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
local CAMERA_PATH = os.getenv("VON_CAMERA_LOG")
local SECONDS = tonumber(os.getenv("VON_ACTION_SECONDS") or "40")
local START_FRAME = tonumber(os.getenv("VON_ACTION_START_FRAME") or "2120")
local CYCLES = tonumber(os.getenv("VON_ACTION_CYCLES") or "2")
local COIN_FRAME = tonumber(os.getenv("VON_PROGRESS_COIN_FRAME") or "900")
local MATCH_START = tonumber(os.getenv("VON_PROGRESS_START_FRAME") or "1500")
-- Optional machine-select navigation: press "right" SELECT_STEPS times after
-- the coin before confirming, so P1 is that roster entry (0 = default Temjin,
-- unchanged). Mirrors capture_single_player.lua's machine_select phase.
local SELECT_STEPS = tonumber(os.getenv("VON_ACTION_SELECT_STEPS") or "0")
local SELECT_SETTLE = 180
local SELECT_STEP_FRAMES = 45
-- Lab-only placement for close-range recovery.  The normal movement schedule
-- is intentionally preserved for locomotion clips, but melee clips must be
-- captured inside the game's near-lock radius or they silently become idle.
local CLOSE_RANGE_DISTANCE = tonumber(os.getenv("VON_ACTION_CLOSE_RANGE") or "8")
local REACTION_DISTANCE = tonumber(os.getenv("VON_REACTION_DISTANCE") or "0")

local log_file = assert(io.open(LOG_PATH, "w"))
log_file:write("action: session start\n")
log_file:flush()
local lock_file = LOCK_PATH and assert(io.open(LOCK_PATH, "w")) or nil
if lock_file then lock_file:write("lock: session start\n") lock_file:flush() end
local camera_file = CAMERA_PATH and assert(io.open(CAMERA_PATH, "w")) or nil
if camera_file then camera_file:write("camera: session start\n") camera_file:flush() end

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
    { "reaction_probe", 7200, {} },
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

local function read_f32(addr)
    return (string.unpack("<f", string.pack("<I", read_u32(addr))))
end

local function float_bits(value)
    return string.unpack("<I", string.pack("<f", value))
end

local function write_f32(addr, value)
    local ok = pcall(function() space:write_u32(addr, float_bits(value)) end)
    return ok
end

local function setup_close_range(action)
    if action ~= "melee_stab" and action ~= "melee_cross_slash" then return end
    -- Keep the player's current side of the opponent, close enough for melee
    -- but not overlapping.  Preserve the opponent's coordinates and place the
    -- player on +X; this is a capture-lab setup, never runtime game logic.
    local ex = read_f32(0x005040d8)
    local ez = read_f32(0x005040e0)
    local px = ex + CLOSE_RANGE_DISTANCE
    local pz = ez
    local heading = math.deg(math.atan(ez - pz, ex - px))
    write_f32(0x00503ad8, px)
    write_f32(0x00503ae0, pz)
    write_f32(0x00503c28, heading)
    log(string.format(
        "action: close_range action=%s px=%.4f pz=%.4f ex=%.4f ez=%.4f distance=%.4f",
        action, px, pz, ex, ez, math.sqrt((px - ex) * (px - ex) + (pz - ez) * (pz - ez))))
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
    local selector = read_u16(0x00503ad0 + 0x174)
    local state = read_u16(0x00503ad0 + 0x176)
    local object_state = read_u16(0x00503ad0 + 0x172)
    local object_mode = read_u32(0x00503ad0 + 0x64)
    local cursor = read_u16(0x00503ad0 + 0x17a)
    local health = read_u16(0x00503ad0 + 0x1d0)
    local enemy_health = read_u16(0x005040d0 + 0x1d0)
    local command = read_u16(0x00503ad0 + 0x108)
    lock_file:write(string.format(
        "lock: t=%.6f frame=%d action=%s mode=%08x px=%08x pz=%08x ex=%08x ez=%08x head=%08x pa0=%04x body=%08x paired=%08x sel=%04x state=%04x objstate=%04x objmode=%08x cur=%04x hp=%04x ehp=%04x cmd=%04x\n",
        now(), frame, current, mode, px or 0, pz or 0, ex or 0, ez or 0,
        head or 0, pa0 or 0, body or 0, paired or 0,
        selector or 0, state or 0, object_state or 0, object_mode or 0, cursor or 0,
        health or 0, enemy_health or 0, command or 0))
    lock_file:flush()
end

-- Per-frame camera extrinsics (recovered-camera.md): eye and target in world
-- space. The traced geometry matrices are camera-relative, so this is what lets
-- a capture be converted back to model space.
local function log_camera()
    if not camera_file then return end
    local ex = read_f32(0x00504b98)  -- eye
    local ey = read_f32(0x00504b9c)
    local ez = read_f32(0x00504ba0)
    local tx = read_f32(0x00504bb4)  -- target
    local ty = read_f32(0x00504bb8)
    local tz = read_f32(0x00504bbc)
    local dist = read_f32(0x00504bc8)
    camera_file:write(string.format(
        "camera: t=%.6f frame=%d action=%s eye=%.6f,%.6f,%.6f target=%.6f,%.6f,%.6f dist=%.6f\n",
        now(), frame, current, ex, ey, ez, tx, ty, tz, dist))
    camera_file:flush()
end

local function open_window()
    local entry = CYCLE[schedule_pos]
    local name, frames, keys = entry[1], entry[2], entry[3]
    release_all()
    for _, k in ipairs(keys) do set_key(k, true) end
    current = name
    window_end = frame + frames
    log(string.format("action: t=%.6f frame=%d action=%s begin", now(), frame, name))
    if name == "reaction_probe" and REACTION_DISTANCE > 0 then
        local ex = read_f32(0x005040d8)
        local ez = read_f32(0x005040e0)
        write_f32(0x00503ad8, ex + REACTION_DISTANCE)
        write_f32(0x00503ae0, ez)
        log(string.format("action: reaction placement distance=%.3f", REACTION_DISTANCE))
    end
    setup_close_range(name)
    schedule_pos = schedule_pos + 1
    if schedule_pos > #CYCLE then
        schedule_pos = 1
        cycles_done = cycles_done + 1
    end
end

local function boot_step()
    if frame < START_FRAME then
        set_key("coin", frame == COIN_FRAME)
        if SELECT_STEPS <= 0 then
            set_key("start", frame == MATCH_START)
        else
            -- Walk the select cursor, finishing the last step before the
            -- confirm at MATCH_START; 8-frame presses match the harness.
            local base = MATCH_START - (SELECT_STEPS + 1) * SELECT_STEP_FRAMES
            local right = false
            for step = 1, SELECT_STEPS do
                local at = base + step * SELECT_STEP_FRAMES
                if frame >= at and frame < at + 8 then right = true end
            end
            set_key("right", right)
            set_key("start", frame == MATCH_START)
        end
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
    if camera_file and schedule_active then log_camera() end
end)
