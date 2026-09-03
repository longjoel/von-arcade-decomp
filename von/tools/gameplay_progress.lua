-- Scripted attract-to-gameplay progression for the Virtual-On MAME driver.
--
-- Reads the confirmed 64x64 text tilemap at bus address 0x01000000 through the
-- i960 program space (tile value = 0x8000 | ASCII) and drives IN0/IN1/IN2
-- fields directly, so host keyboard mapping quirks are irrelevant.
--
-- Confirmed flow (vonj-progress traces and snapshots):
--   warning auto-dismisses, attract runs, a Coin 1 pulse at ~frame 900 opens
--   MACHINE SELECT, and 1 Player Start at ~frame 1500 confirms the highlighted
--   machine. The game then runs its brief pre-match scene before the first
--   deterministic battle (the first opponent and arena are fixed).
-- An optional combat phase can cycle stick directions and pulse both shot
-- triggers for general trace coverage; disable it when capturing the untouched
-- first-match scene with VON_PROGRESS_COMBAT=0.
--
-- Every tilemap checksum change and input press is logged. emu.print_info
-- does not reach -oslog, so we write our own log file.
-- Environment: VON_PROGRESS_SECONDS (default 150 emulated seconds)
--              VON_PROGRESS_LOG     (log file path)
--              VON_PROGRESS_COMBAT  (default 1; set 0 for passive capture)
--              VON_PROGRESS_COMBAT_START (default 1800)
--              VON_PROGRESS_SELECT_STEPS (right presses before confirmation)
--              VON_PROGRESS_AUTO_START (default 1; set 0 for selector-only capture)
--              VON_PROGRESS_GEOMETRY_STATE_LOG (optional state log path)

local SECONDS = tonumber(os.getenv("VON_PROGRESS_SECONDS") or "150")
local TARGET_FRAMES = SECONDS * 60
local CAPTURE_START_FRAME = tonumber(os.getenv("VON_PROGRESS_CAPTURE_START_FRAME") or "0")
local LOG_PATH = os.getenv("VON_PROGRESS_LOG") or "vonj-progress-lua.log"
local GEOMETRY_STATE_LOG_PATH = os.getenv("VON_PROGRESS_GEOMETRY_STATE_LOG")

local TILE_BASE = 0x01000000
local ROWS = 64
local COLS = 64

local log_file = assert(io.open(LOG_PATH, "w"))
log_file:write("progress: session start\n")
log_file:flush()

local geometry_state_file
if GEOMETRY_STATE_LOG_PATH then
    geometry_state_file = assert(io.open(GEOMETRY_STATE_LOG_PATH, "w"))
    geometry_state_file:write("geometry-state: session start\n")
    geometry_state_file:flush()
end

local function log(message)
    log_file:write(message .. "\n")
    log_file:flush()
end

local function log_geometry_state(message)
    if geometry_state_file then
        geometry_state_file:write(message .. "\n")
        geometry_state_file:flush()
    end
end

local frame = 0
local space
local fields = {}
local last_screen_hash = nil
local pressed_until = {}
local last_geometry_state

local function geometry_state()
    if not space or not geometry_state_file then
        return
    end
    local function read_word(address)
        local ok, value = pcall(function() return space:read_u32(address) end)
        if ok then
            return value
        end
        return 0xffffffff
    end
    local function read_byte(address)
        local ok, value = pcall(function() return space:read_u8(address) end)
        if ok then
            return value
        end
        return 0xff
    end
    -- These are the host-side state words consumed by 0x6f6f0 after its
    -- opcode-0x41 lookup: mode, callback byte-map base, selected record
    -- table, alternate record field, and the two output mask globals.
    local values = {
        mode = space:read_u32(0x005770f0),
        byte_map = space:read_u32(0x0051bb20),
        records = space:read_u32(0x0051bb24),
        record_aux = space:read_u32(0x0051bb28),
        mask_special = space:read_u32(0x00562c80),
        mask_general = space:read_u32(0x00562c84),
    }
    local record_words = {}
    for _, selector in ipairs({ 0, 6, 13 }) do
        local base = values.records + selector * 20
        local words = {}
        for offset = 0, 16, 4 do
            words[#words + 1] = read_word(base + offset)
        end
        record_words[#record_words + 1] = string.format(
            "%d:%08x,%08x,%08x,%08x,%08x", selector,
            words[1], words[2], words[3], words[4], words[5])
    end
    local map_bytes = {}
    for offset = 0, 31 do
        map_bytes[#map_bytes + 1] = string.format(
            "%02x", read_byte(values.byte_map + offset))
    end
    local state = string.format(
        "%08x/%08x/%08x/%08x/%08x/%08x/%s/%s",
        values.mode, values.byte_map, values.records, values.record_aux,
        values.mask_special, values.mask_general,
        table.concat(record_words, "/"), table.concat(map_bytes))
    if state ~= last_geometry_state then
        log_geometry_state(string.format(
            "geometry-state: frame %d mode=%08x byte_map=%08x records=%08x " ..
            "record_aux=%08x mask_special=%08x mask_general=%08x " ..
            "records012: %s map[0:32]=%s",
            frame, values.mode, values.byte_map, values.records,
            values.record_aux, values.mask_special, values.mask_general,
            table.concat(record_words, "/"), table.concat(map_bytes)))
        last_geometry_state = state
    end
end

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

-- Boot inputs. Defaults preserve the confirmed flow; delayed captures can hold
-- the attract screen until a requested frame before injecting coin/start.
local SELECT_STEPS = tonumber(os.getenv("VON_PROGRESS_SELECT_STEPS") or "0")
local AUTO_START = os.getenv("VON_PROGRESS_AUTO_START") ~= "0"
local COIN_FRAME = tonumber(os.getenv("VON_PROGRESS_COIN_FRAME") or "900")
local START_FRAME = tonumber(os.getenv("VON_PROGRESS_START_FRAME") or "1500")
local schedule = { { frame = COIN_FRAME, key = "coin" } }
for step = 1, SELECT_STEPS do
    schedule[#schedule + 1] = { frame = START_FRAME - 420 + step * 45, key = "right" }
end
if AUTO_START then
    schedule[#schedule + 1] = { frame = START_FRAME + SELECT_STEPS * 45, key = "start" }
end
local schedule_index = 1

-- Combat phase: cycle the left stick around the compass and pulse both shot
-- triggers so movement, targeting, and weapon code paths all execute.
local COMBAT_ENABLED = os.getenv("VON_PROGRESS_COMBAT") ~= "0"
local COMBAT_START = tonumber(os.getenv("VON_PROGRESS_COMBAT_START") or "1800")
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
        if step.key == "start" then
            log("progress: machine selection confirmed; pre-match scene begins")
        end
        press(step.key, frame + 8)
        schedule_index = schedule_index + 1
    end

    -- Input may establish the requested checkpoint before evidence begins.
    -- This lets a run press START on machine select and capture only the
    -- resulting takeoff/intro/match transition.
    if frame < CAPTURE_START_FRAME then
        return
    end

    if COMBAT_ENABLED and frame >= COMBAT_START and frame <= COMBAT_END then
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
        geometry_state()
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
