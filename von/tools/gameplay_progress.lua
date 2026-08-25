-- Scripted attract-to-gameplay progression for the Virtual-On MAME driver.
--
-- Reads the confirmed 64x64 text tilemap at bus address 0x01000000 through the
-- i960 program space (tile value = 0x8000 | ASCII) and drives IN0/IN1/IN2
-- fields directly, so host keyboard mapping quirks are irrelevant.
--
-- Confirmed flow (vonj-progress traces and snapshots):
--   warning auto-dismisses, attract runs, a Coin 1 pulse at ~frame 900 opens
--   MACHINE SELECT, 1 Player Start at ~frame 1500 confirms the highlighted
--   machine and launches the battle; the battle times out around frame 7000.
-- A combat phase then cycles stick directions and pulses both shot triggers
-- so game-logic and geometry paths stay active for trace coverage.
--
-- Every tilemap checksum change and input press is logged. emu.print_info
-- does not reach -oslog, so we write our own log file.
-- Environment: VON_PROGRESS_SECONDS (default 150 emulated seconds)
--              VON_PROGRESS_LOG     (log file path)

local SECONDS = tonumber(os.getenv("VON_PROGRESS_SECONDS") or "150")
local TARGET_FRAMES = SECONDS * 60
local LOG_PATH = os.getenv("VON_PROGRESS_LOG") or "vonj-progress-lua.log"

local TILE_BASE = 0x01000000
local ROWS = 64
local COLS = 64

local log_file = assert(io.open(LOG_PATH, "w"))
log_file:write("progress: session start\n")
log_file:flush()

local function log(message)
    log_file:write(message .. "\n")
    log_file:flush()
end

local frame = 0
local space
local fields = {}
local last_screen_hash = nil
local pressed_until = {}

-- Confirmed field names on the vonj driver (IN0/IN1/IN2).
local FIELD_NAMES = {
    coin       = { ":IN0", "Coin 1" },
    start      = { ":IN0", "1 Player Start" },
    down       = { ":IN1", "P1 Left Stick/Down" },
    up         = { ":IN1", "P1 Left Stick/Up" },
    right      = { ":IN1", "P1 Left Stick/Right" },
    left       = { ":IN1", "P1 Left Stick/Left" },
    left_shot  = { ":IN1", "P1 Left Shot" },
    left_dash  = { ":IN1", "P1 Left Dash" },
    right_shot = { ":IN2", "P1 Right Shot" },
    right_dash = { ":IN2", "P1 Right Dash" },
}

local function setup()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then
        return false
    end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    if not space then
        log("progress: no program space")
        return false
    end
    for key, spec in pairs(FIELD_NAMES) do
        local port = manager.machine.ioport.ports[spec[1]]
        fields[key] = port and port.fields[spec[2]] or nil
    end
    for _, key in ipairs({ "coin", "start", "left_shot" }) do
        if not fields[key] then
            log("progress: missing required field " .. key)
            return false
        end
    end
    log("progress: fields resolved")
    return true
end

local function press(key, until_frame)
    local f = fields[key]
    if not f then
        return
    end
    pressed_until[key] = until_frame
    f:set_value(1)
end

local function release_expired()
    for key, until_frame in pairs(pressed_until) do
        if frame >= until_frame then
            local f = fields[key]
            if f then
                f:clear_value()
            end
            pressed_until[key] = nil
        end
    end
end

local function screen_text()
    -- Decode printable 0x8000-flagged tiles into trimmed rows.
    local rows = {}
    for row = 0, ROWS - 1 do
        local chars = {}
        local base = TILE_BASE + row * COLS * 2
        for col = 0, COLS - 1 do
            local v = space:read_u16(base + col * 2)
            local c = v & 0x7fff
            if (v & 0x8000) ~= 0 and c >= 0x20 and c < 0x7f then
                chars[#chars + 1] = string.char(c)
            else
                chars[#chars + 1] = " "
            end
        end
        rows[#rows + 1] = table.concat(chars):gsub("%s+$", "")
    end
    return table.concat(rows, "\n")
end

local function tile_checksum()
    -- Whole-tilemap FNV-1a; detects graphics-only screen changes that the
    -- ASCII text decoder cannot see.
    local hash = 2166136261
    for i = 0, ROWS * COLS - 1 do
        local v = space:read_u16(TILE_BASE + i * 2)
        hash = (hash ~ v) * 16777619 % 4294967296
    end
    return hash
end

-- Boot inputs. Coin at ~frame 900 opens MACHINE SELECT; start at ~frame 1500
-- confirms the highlighted machine and launches the battle.
local schedule = {
    { frame = 900,  key = "coin" },
    { frame = 1500, key = "start" },
}
local schedule_index = 1

-- Combat phase: cycle the left stick around the compass and pulse both shot
-- triggers so movement, targeting, and weapon code paths all execute.
local COMBAT_START = 1800
local COMBAT_END = 7000
local DIRECTIONS = { "up", "right", "down", "left" }

emu.register_periodic(function()
    frame = frame + 1
    if not space and frame % 60 == 1 then
        if not setup() then
            return
        end
    end
    if not space or not fields.coin then
        return
    end

    release_expired()

    while schedule_index <= #schedule and frame >= schedule[schedule_index].frame do
        local step = schedule[schedule_index]
        log(string.format("progress: frame %d press %s", frame, step.key))
        press(step.key, frame + 8)
        schedule_index = schedule_index + 1
    end

    if frame >= COMBAT_START and frame <= COMBAT_END then
        -- Change held direction every 120 frames.
        if frame % 120 == 0 then
            local key = DIRECTIONS[(math.floor(frame / 120) % #DIRECTIONS) + 1]
            log(string.format("progress: frame %d move %s", frame, key))
            press(key, frame + 120)
        end
        -- Pulse dashes every 180 frames and shots every 45 frames.
        if frame % 180 == 0 then
            local key = (math.floor(frame / 180) % 2) == 0 and "left_dash"
                or "right_dash"
            press(key, frame + 10)
        end
        if frame % 45 == 0 then
            local key = (math.floor(frame / 45) % 2) == 0 and "left_shot"
                or "right_shot"
            press(key, frame + 20)
        end
    end

    -- Poll the tilemap once per second: checksum change detection plus any
    -- ASCII text overlay.
    if frame % 30 == 0 then
        local ok, sum = pcall(tile_checksum)
        if ok then
            if sum ~= last_screen_hash then
                last_screen_hash = sum
                local text_ok, text = pcall(screen_text)
                if text_ok and text:match("%S") then
                    log(string.format(
                        "progress: frame %d checksum %08x TEXT >>>\n%s\n<<< END",
                        frame, sum, text))
                else
                    log(string.format("progress: frame %d checksum %08x (graphics)",
                        frame, sum))
                end
            end
            -- Snapshot every second so menu flow can be reviewed visually.
            pcall(function() manager.machine.video:snapshot() end)
        else
            log("progress: checksum read failed at frame " .. frame)
        end
    end

    if frame >= TARGET_FRAMES then
        log("progress: session complete at frame " .. frame)
        manager.machine:exit()
    end
end)
