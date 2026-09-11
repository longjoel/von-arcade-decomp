-- Passive recorder for human-instrumented captures.
--
-- Drives NO inputs: a human joins and plays through the real menus while
-- this script records everything the join tools consume (same line formats
-- as fuzz_battle_ram.lua, so extract/annotate/join work unchanged):
--   - battle-long RAM state series (VON_RECORD_STATELOG, multi-spec)
--   - full-region snapshots every VON_RECORD_SNAP_EVERY_S seconds
--   - tilemap-checksum flow log (menu/battle transitions)
--   - event marks: rising edges on the marker field (default Coin 2 --
--     harmless in single-player). The human taps the marker key at battle
--     start, each jump-apex attempt, each felt lock, and round end.
--
-- Environment:
--   VON_RECORD_LOG          log file path (required)
--   VON_RECORD_SNAP_DIR     snapshot directory (required)
--   VON_RECORD_STATELOG     "base,len,every[;...]" (default cells+workspaces)
--   VON_RECORD_SNAP_EVERY_S snapshot period in seconds (default 10)
--   VON_RECORD_MARKER       ioport field path "PORT:name" (default ":IN0:Coin 2")
--   VON_RECORD_EXIT_FRAME   exit at this frame, 0 = run until closed (default 0)
--   VON_RECORD_MACRO_HOLD_FRAMES  hold the marker key this many frames to
--                                 toggle macro capture (default 45, ~0.75s).
--                                 Captures go to <snapdir>/../macro.txt as
--                                 "start <frame>" then "<frame> <mask>" rows.
--   VON_RECORD_MACRO_PLAY   replay a macro file (drives the 12 P1 fields)
--   VON_RECORD_MACRO_PLAY_PRESERVE_TIMING=1 replay at recorded frame numbers
--   VON_RECORD_MACRO_PLAY_FRAME_OFFSET add this local-frame offset when
--                              matching preserved macro rows after a state load
--   VON_RECORD_MACRO_PLAY_CLEAR_MASK clear selected playback bits (hex),
--                              useful for shot/no-shot differential captures
--   VON_RECORD_MACRO_PLAY_FORCE_MASK set selected playback bits (hex) after
--                              clearing, for matched input-control captures
--   VON_RECORD_MACRO_PLAY_LOG_FROM/TO log applied masks and actual port reads
--   VON_RECORD_BOOTSTRAP=1 drive the known coin/select/start sequence before
--   VON_RECORD_LOAD_STATE=<name> schedule a state load from the recorder
--                              macro playback (useful for replaying a human
--                              macro captured after the player joined)
--   VON_RECORD_SHOT_PROBE_FROM/TO/INTERVAL/HOLD drive active-low P1 Left Shot
--                              on a relative frame schedule after a state load
--   VON_RECORD_SAVE_STATE_FRAME save asynchronously at this recorder frame
--   VON_RECORD_SAVE_STATE_NAME state filename (default mcp-checkpoint)
--   VON_RECORD_WEAPON_LOG=1 log the three weapon bytes and availability bytes
--                            every frame (optionally bounded by *_FROM/_TO)
--   VON_WATCH_WRITES        "base,len[;...]" write-watch windows for writer
--                           PC capture (default off). Each window gets a
--                           passive write tap; distinct writer PCs per
--                           window are counted and summarized as watch:
--                           lines every 600 frames and at session end.
--                           Example: VON_WATCH_WRITES="0x503CB8,0x4"
--   VON_WATCH_STRUCT_FIELDS=1 scan writes for recovered input/status byte
--                            offsets 0x4c/0x4d and 0x52..0x55
local LOG_PATH = assert(os.getenv("VON_RECORD_LOG"), "VON_RECORD_LOG is required")
local SNAP_DIR = assert(os.getenv("VON_RECORD_SNAP_DIR"), "VON_RECORD_SNAP_DIR is required")
local SNAP_EVERY = tonumber(os.getenv("VON_RECORD_SNAP_EVERY_S") or "10") or 10
local EXIT_FRAME = tonumber(os.getenv("VON_RECORD_EXIT_FRAME") or "0") or 0

local MARKER_PORT, MARKER_NAME = (os.getenv("VON_RECORD_MARKER") or ":IN0:Coin 2"):match("^([^:]*:[^:]*):(.*)$")

-- Macro record hotkey: holding the marker key past MACRO_HOLD_FRAMES toggles
-- per-frame capture of the P1 input mask (rising edge still logs one mark).
-- VON_RECORD_MACRO_PLAY=<file> replays a capture (drives the same fields).
local MACRO_HOLD_FRAMES = tonumber(os.getenv("VON_RECORD_MACRO_HOLD_FRAMES") or "45") or 45
local MACRO_PLAY_PATH = os.getenv("VON_RECORD_MACRO_PLAY")
local MACRO_START = os.getenv("VON_RECORD_MACRO_START") == "1"
local BOOTSTRAP = os.getenv("VON_RECORD_BOOTSTRAP") == "1"
local LOAD_STATE = os.getenv("VON_RECORD_LOAD_STATE")
local LOAD_STATE_DONE = false
local MACRO_PLAY_CLEAR_MASK = tonumber(os.getenv("VON_RECORD_MACRO_PLAY_CLEAR_MASK") or "0") or 0
local MACRO_PLAY_FORCE_MASK = tonumber(os.getenv("VON_RECORD_MACRO_PLAY_FORCE_MASK") or "0") or 0
local MACRO_PLAY_LOG_FROM = tonumber(os.getenv("VON_RECORD_MACRO_PLAY_LOG_FROM") or "-1") or -1
local MACRO_PLAY_LOG_TO = tonumber(os.getenv("VON_RECORD_MACRO_PLAY_LOG_TO") or "-1") or -1
local SHOT_PROBE_FROM = tonumber(os.getenv("VON_RECORD_SHOT_PROBE_FROM") or "-1") or -1
local SHOT_PROBE_TO = tonumber(os.getenv("VON_RECORD_SHOT_PROBE_TO") or "-1") or -1
local SHOT_PROBE_INTERVAL = tonumber(os.getenv("VON_RECORD_SHOT_PROBE_INTERVAL") or "0") or 0
local SHOT_PROBE_HOLD = tonumber(os.getenv("VON_RECORD_SHOT_PROBE_HOLD") or "1") or 1
local SHOT_PROBE_FORCE_OFF = os.getenv("VON_RECORD_SHOT_PROBE_FORCE_OFF") == "1"
local SAVE_STATE_FRAME = tonumber(os.getenv("VON_RECORD_SAVE_STATE_FRAME") or "-1") or -1
local SAVE_STATE_NAME = os.getenv("VON_RECORD_SAVE_STATE_NAME") or "mcp-checkpoint"
local save_state_done = false
local WEAPON_LOG = os.getenv("VON_RECORD_WEAPON_LOG") == "1"
local WEAPON_LOG_FROM = tonumber(os.getenv("VON_RECORD_WEAPON_LOG_FROM") or "0") or 0
local WEAPON_LOG_TO = tonumber(os.getenv("VON_RECORD_WEAPON_LOG_TO") or "0") or 0
local DEFER_AFTER_STATE = os.getenv("VON_RECORD_DEFER_AFTER_STATE") == "1"
-- Bit order (also the playback column order): IN1 shot, dash, up, down,
-- left, right, then IN2 shot, dash, up, down, left, right.
local MACRO_FIELDS = {
    { ":IN1", "P1 Left Shot" }, { ":IN1", "P1 Left Dash" },
    { ":IN1", "P1 Left Stick/Up" }, { ":IN1", "P1 Left Stick/Down" },
    { ":IN1", "P1 Left Stick/Left" }, { ":IN1", "P1 Left Stick/Right" },
    { ":IN2", "P1 Right Shot" }, { ":IN2", "P1 Right Dash" },
    { ":IN2", "P1 Right Stick/Up" }, { ":IN2", "P1 Right Stick/Down" },
    { ":IN2", "P1 Right Stick/Left" }, { ":IN2", "P1 Right Stick/Right" },
}

local REGIONS = {
    { 0x515000, 0x4000 },
    { 0x504c80, 0x400 },
    { 0x5039c0, 0x300 },
    { 0x500000, 0x6000 },
}
local ROWS, COLS, TILE_BASE = 48, 64, 0x500000

local STATELOGS = {}
do
    local raw = os.getenv("VON_RECORD_STATELOG") or "0x504c80,0x400,2;0x5039c0,0x300,5"
    for spec in string.gmatch(raw, "([^;]+)") do
        local parts = {}
        for tok in string.gmatch(spec, "([^,]+)") do parts[#parts + 1] = tok end
        if #parts == 3 then
            STATELOGS[#STATELOGS + 1] = {
                base = tonumber(parts[1]),
                len = tonumber(parts[2]),
                every = tonumber(parts[3]),
            }
        end
    end
end

local WATCHES = {}
do
    local raw = os.getenv("VON_WATCH_WRITES") or ""
    for spec in string.gmatch(raw, "([^;]+)") do
        local parts = {}
        for tok in string.gmatch(spec, "([^,]+)") do parts[#parts + 1] = tok end
        if #parts == 2 then
            local base, len = tonumber(parts[1]), tonumber(parts[2])
            if base and len and len > 0 then
                WATCHES[#WATCHES + 1] = { base = base, len = len }
            end
        end
    end
end
local WATCH_LOG = os.getenv("VON_WATCH_LOG_WRITES") == "1"
local WATCH_LOG_FROM = tonumber(os.getenv("VON_WATCH_LOG_FROM") or "0") or 0
local WATCH_LOG_TO = tonumber(os.getenv("VON_WATCH_LOG_TO") or "0") or 0
local WATCH_STRUCT_FIELDS = os.getenv("VON_WATCH_STRUCT_FIELDS") == "1"
local WATCH_PLAYER_FIELDS = os.getenv("VON_WATCH_PLAYER_FIELDS") == "1"
local WATCH_PLAYER_BASE = tonumber(os.getenv("VON_WATCH_PLAYER_BASE") or "")

local log_file = assert(io.open(LOG_PATH, "w"))
local function log(message)
    log_file:write(message .. "\n")
    log_file:flush()
end
log(string.format("watch: configured %d window(s) from %s", #WATCHES,
    os.getenv("VON_WATCH_WRITES") or "<unset>"))

local frame = 0
local space = nil
local marker = nil
local marker_port = nil
local marker_mask = nil
local marker_def = nil
local marker_last = 0
local mark_count = 0
local last_screen_hash = nil

local function statelog(spec)
    local words = {}
    for addr = spec.base, spec.base + spec.len - 1, 4 do
        local ok, v = pcall(function() return space:read_u32(addr) end)
        words[#words + 1] = ok and string.format("%08x", v) or "????????"
    end
    log(string.format("fuzz: state f%d @%08x %s", frame, spec.base,
        table.concat(words, " ")))
end

local function weapon_log()
    if not WEAPON_LOG or not space or frame < WEAPON_LOG_FROM
        or (WEAPON_LOG_TO > 0 and frame > WEAPON_LOG_TO) then
        return
    end
    local resources, availability = {}, {}
    for _, addr in ipairs({ 0x503c08, 0x503c09, 0x503c0a,
                            0x503cad, 0x503cae, 0x503caf }) do
        local ok, value = pcall(function() return space:read_u8(addr) end)
        if not ok then value = 0 end
        if addr <= 0x503c0a then
            resources[#resources + 1] = string.format("%02x", value)
        else
            availability[#availability + 1] = string.format("%02x", value)
        end
    end
    log(string.format("weapon: f%d resources=%s availability=%s", frame,
        table.concat(resources, ","), table.concat(availability, ",")))
end

local function snapshot(tag)
    for _, region in ipairs(REGIONS) do
        local base, len = region[1], region[2]
        local out = assert(io.open(string.format("%s/snap-%s-%04x.txt", SNAP_DIR, tag, base), "w"))
        for addr = base, base + len - 1, 4 do
            local ok, v = pcall(function() return space:read_u32(addr) end)
            if ok then
                out:write(string.format("%08x %08x\n", addr, v))
            end
        end
        out:close()
    end
    log(string.format("fuzz: frame %d snapshot %s", frame, tag))
end

local function screen_hash()
    local ok, h = pcall(function()
        local acc = 2166136261
        for i = 0, ROWS * COLS - 1 do
            acc = (acc ~ space:read_u16(TILE_BASE + i * 2)) * 16777619 % 4294967296
        end
        return acc
    end)
    if ok then return h end
    return nil
end

-- Writer-PC watch: passive write taps over WATCHES windows. The tap
-- callback returns data unchanged; it only attributes each write to the
-- maincpu CURPC at tap time. Counts accumulate in watch_pcs and are
-- emitted as watch: summaries (never per-write, to avoid log floods).
local cpu_dev = nil
local watch_taps = {}
local watch_pcs = {}
local WATCH_MAX_PCS = 64

local function install_watches()
    if #WATCHES == 0 or not space then return end
    for _, w in ipairs(WATCHES) do
        watch_pcs[w.base] = { _n = 0 }
        local ok, tap = pcall(function()
            return space:install_write_tap(w.base, w.base + w.len - 1,
                string.format("watch%08x", w.base),
                function(offset, data, mask)
                    local seen = watch_pcs[w.base]
                    if seen and cpu_dev then
                        local pc = "?"
                        local okc, st = pcall(function()
                            return cpu_dev.state["CURPC"].value
                        end)
                        if okc and type(st) == "number" then
                            pc = string.format("0x%x", st)
                        end
                        if not seen[pc] then
                            if seen._n >= WATCH_MAX_PCS then return data end
                            seen[pc] = 0
                            seen._n = seen._n + 1
                        end
                        seen[pc] = seen[pc] + 1
                        if WATCH_LOG and frame >= WATCH_LOG_FROM
                            and (WATCH_LOG_TO == 0 or frame <= WATCH_LOG_TO) then
                            log(string.format("watchwrite f%d @%08x pc=%s data=%08x mask=%08x",
                                frame, offset, pc, data, mask or 0))
                        end
                    end
                    return data
                end)
        end)
        if ok and tap then watch_taps[#watch_taps + 1] = tap end
    end
    log(string.format("watch: %d window(s) armed (%d taps installed)",
        #WATCHES, #watch_taps))
end

local function watch_summary(tag)
    for _, w in ipairs(WATCHES) do
        local pcs = {}
        for pc, n in pairs(watch_pcs[w.base] or {}) do
            if pc ~= "_n" then pcs[#pcs + 1] = string.format("%s(x%d)", pc, n) end
        end
        table.sort(pcs)
        log(string.format("watch: @%08x %s writers=%d %s",
            w.base, tag, #pcs, table.concat(pcs, " ")))
    end
end

-- The input-maintenance routine at i960 0x26404 operates on a player/status
-- structure whose useful byte offsets are 0x4c/0x4d and 0x52..0x55. The
-- structure base is runtime-owned, so use a short-lived filtered tap over
-- main RAM to discover its absolute address during a focused MCP run.
local function install_struct_field_watch()
    if (not WATCH_STRUCT_FIELDS and not WATCH_PLAYER_FIELDS) or WATCH_PLAYER_BASE or not space then return end
    -- MAME exposes these i960 byte stores through the aligned 32-bit bus
    -- location (0x4c, 0x50, or 0x54) plus a byte mask.
    local fields = { [0x4c] = true, [0x50] = true, [0x54] = true }
    local ok, tap = pcall(function()
        return space:install_write_tap(0x500000, 0x51ffff,
            "recovered-input-status-fields",
            function(offset, data, mask)
                local pc = 0
                if cpu_dev then
                    local okc, st = pcall(function()
                        return cpu_dev.state["CURPC"].value
                    end)
                    if okc and type(st) == "number" then pc = st end
                end
                local field_match = fields[offset & 0xff]
                local routine_match = (pc >= 0x26300 and pc <= 0x266ff)
                    or (pc >= 0x73000 and pc <= 0x733ff)
                if (field_match or routine_match) and frame >= WATCH_LOG_FROM
                    and (WATCH_LOG_TO == 0 or frame <= WATCH_LOG_TO) then
                    local label = routine_match and "structroutine" or "structfield"
                    log(string.format("%s f%d @%08x pc=0x%x data=%08x mask=%08x",
                        label, frame, offset, pc, data, mask or 0))
                end
                return data
            end)
    end)
    if ok and tap then
        watch_taps[#watch_taps + 1] = tap
        log("watch: recovered input/status field scan armed")
    else
        log("watch: recovered input/status field scan unavailable")
    end
    local okr, rtap = pcall(function()
        return space:install_read_tap(0x500000, 0x51ffff,
            "recovered-input-status-reads",
            function(offset, data, mask)
                local pc = 0
                if cpu_dev then
                    local okc, st = pcall(function()
                        return cpu_dev.state["CURPC"].value
                    end)
                    if okc and type(st) == "number" then pc = st end
                end
                if ((pc >= 0x26300 and pc <= 0x266ff)
                    or (pc >= 0x73000 and pc <= 0x733ff))
                    and frame >= WATCH_LOG_FROM
                    and (WATCH_LOG_TO == 0 or frame <= WATCH_LOG_TO) then
                    log(string.format("structread f%d @%08x pc=0x%x data=%08x mask=%08x",
                        frame, offset, pc, data, mask or 0))
                end
                if WATCH_PLAYER_FIELDS and pc == 0x73014 and frame >= WATCH_LOG_FROM
                    and (WATCH_LOG_TO == 0 or frame <= WATCH_LOG_TO) then
                    local function state_value(name)
                        local okv, value = pcall(function()
                            return cpu_dev.state[name].value
                        end)
                        return okv and type(value) == "number" and value or nil
                    end
                    local r4 = state_value("R4") or state_value("r4")
                    local g7 = state_value("G7") or state_value("g7")
                    if r4 then
                        local function word(addr)
                            local okw, value = pcall(function()
                                return space:read_u32(addr)
                            end)
                            return okw and value or 0
                        end
                        local fields = {
                            r4, g7 or 0, word(r4 + 0x170), word(r4 + 0x172),
                            word(r4 + 0x184), word(r4 + 0x1f0)
                        }
                        local changed = not last_player_fields
                        if not changed then
                            for i = 1, #fields do
                                if fields[i] ~= last_player_fields[i] then
                                    changed = true
                                    break
                                end
                            end
                        end
                        if changed then
                            log(string.format(
                                "playerfields f%d r4=%08x g7=%s +170=%08x +172=%08x +184=%08x +1f0=%08x",
                                frame, r4, g7 and string.format("%08x", g7) or "?",
                                fields[3], fields[4], fields[5], fields[6]))
                            last_player_fields = fields
                        end
                    end
                end
                return data
            end)
    end)
    if okr and rtap then
        watch_taps[#watch_taps + 1] = rtap
        log("watch: recovered input/status field read scan armed")
    else
        log("watch: recovered input/status field read scan unavailable")
    end
end

local hold_frames, hold_toggled = 0, false
local macro_active, macro_file, macro_handles = false, nil, nil
local macro_start_done = false
local last_player_fields

local function sample_player_fields()
    if not WATCH_PLAYER_BASE or not space or frame < WATCH_LOG_FROM
        or (WATCH_LOG_TO ~= 0 and frame > WATCH_LOG_TO) then
        return
    end
    local function word(addr)
        local ok, value = pcall(function() return space:read_u32(addr) end)
        return ok and value or 0
    end
    local fields = {
        WATCH_PLAYER_BASE,
        word(WATCH_PLAYER_BASE + 0x170),
        word(WATCH_PLAYER_BASE + 0x172),
        word(WATCH_PLAYER_BASE + 0x184),
        word(WATCH_PLAYER_BASE + 0x1f0),
        word(WATCH_PLAYER_BASE + 0x1f4),
        word(WATCH_PLAYER_BASE + 0x1f8)
    }
    local changed = not last_player_fields
    if not changed then
        for i = 1, #fields do
            if fields[i] ~= last_player_fields[i] then changed = true break end
        end
    end
    if changed then
        log(string.format(
            "playerbase f%d r4=%08x +170=%08x +172=%08x +184=%08x +1f0=%08x +1f4=%08x +1f8=%08x",
            frame, fields[1], fields[2], fields[3], fields[4], fields[5], fields[6], fields[7]))
        last_player_fields = fields
    end
end
-- Triple-tap toggle: 3 rising edges within TRIPLE_WINDOW frames toggles too,
-- so a sticky/impulse/jittery field that never reads a sustained level can
-- still arm capture. Jump-apex taps are seconds apart and never qualify.
local TRIPLE_WINDOW = 40
local edge_times = {}
local mark_flash = 0
local macro_path = SNAP_DIR .. "/../macro.txt"
local macro_play_rows, macro_play_idx, macro_play_done = nil, 1, false
local macro_play_preserve = os.getenv("VON_RECORD_MACRO_PLAY_PRESERVE_TIMING") == "1"
local macro_play_frame_offset = tonumber(os.getenv("VON_RECORD_MACRO_PLAY_FRAME_OFFSET") or "0") or 0
local macro_play_logged_fields = false

local bootstrap_schedule = {}
if BOOTSTRAP then
    local coin_frame = tonumber(os.getenv("VON_RECORD_BOOT_COIN_FRAME") or "900")
    local start_frame = tonumber(os.getenv("VON_RECORD_BOOT_START_FRAME") or "1500")
    local steps = tonumber(os.getenv("VON_RECORD_BOOT_SELECT_STEPS") or "2")
    bootstrap_schedule[#bootstrap_schedule + 1] = { frame = coin_frame,
        port = ":IN0", name = "Coin 1", label = "coin" }
    for step = 1, steps do
        bootstrap_schedule[#bootstrap_schedule + 1] = { frame = start_frame - 420 + step * 45,
            port = ":IN1", name = "P1 Left Stick/Right", label = "right" }
    end
    bootstrap_schedule[#bootstrap_schedule + 1] = { frame = start_frame + steps * 45,
        port = ":IN0", name = "1 Player Start", label = "start" }
end
local bootstrap_fields = {}
local bootstrap_pressed_until = {}

local function set_pressed(field, pressed)
    if not field then return end
    local mask = field.mask or 1
    local def = field.defvalue or mask
    local inactive = def & mask
    local active = inactive == 0 and mask or 0
    field:set_value(pressed and active or inactive)
end

-- Macro capture reads whole ports once per frame and bit-tests each
-- field's cached mask (fields have no :read of their own).
local function resolve_macro_fields()
    if macro_handles then return macro_handles end
    macro_handles = {}
    local ports = {}
    for _, spec in ipairs(MACRO_FIELDS) do
        local p = ports[spec[1]]
        if not p then
            pcall(function()
                p = manager.machine.ioport.ports[spec[1]]
            end)
            ports[spec[1]] = p or false
        end
        local field, mask, def = nil, nil, nil
        if p then
            pcall(function()
                field = p.fields[spec[2]]
                if field then mask, def = field.mask, field.defvalue end
            end)
        end
        macro_handles[#macro_handles + 1] = { port = p or nil,
            field = field,
            mask = (type(mask) == "number") and mask or nil,
            def = (type(def) == "number") and def or nil }
    end
    return macro_handles
end

local function resolve_bootstrap_field(spec)
    local key = spec.port .. ":" .. spec.name
    if bootstrap_fields[key] ~= nil then return bootstrap_fields[key] end
    local field
    local port = manager.machine.ioport.ports[spec.port]
    if port then field = port.fields[spec.name] end
    bootstrap_fields[key] = field or false
    return field
end

local function step_bootstrap()
    if not BOOTSTRAP then return end
    for key, until_frame in pairs(bootstrap_pressed_until) do
        if frame >= until_frame then
            local field = bootstrap_fields[key]
            if field then pcall(function() set_pressed(field, false) end) end
            bootstrap_pressed_until[key] = nil
        end
    end
    for _, spec in ipairs(bootstrap_schedule) do
        if frame == spec.frame then
            local field = resolve_bootstrap_field(spec)
            if field then
                set_pressed(field, true)
                bootstrap_pressed_until[spec.port .. ":" .. spec.name] = frame + 8
                log(string.format("bootstrap: frame %d press %s", frame, spec.label))
            else
                log(string.format("bootstrap: missing %s:%s", spec.port, spec.name))
            end
        end
    end
end

local function read_mask()
    local m = 0
    local vals = {}
    for i, h in ipairs(resolve_macro_fields()) do
        if h.port and h.mask and h.def then
            local pv = vals[h.port]
            if pv == nil then
                local ok, v = pcall(function() return h.port:read() end)
                pv = (ok and type(v) == "number") and v or h.def
                vals[h.port] = pv
            end
            if (pv & h.mask) ~= (h.def & h.mask) then m = m | (1 << (i - 1)) end
        end
    end
    return m
end

local function toggle_macro()
    if macro_active then
        macro_active = false
        if macro_file then macro_file:close() macro_file = nil end
        log(string.format("macro f%d stop %s", frame, macro_path))
    else
        pcall(function() os.execute("mkdir -p " .. SNAP_DIR .. "/..") end)
        local f = io.open(macro_path, "a")
        if not f then log("macro: cannot open " .. macro_path) return end
        macro_file = f
        macro_active = true
        macro_file:write(string.format("start %d\n", frame))
        log(string.format("macro f%d start %s", frame, macro_path))
    end
end

if MACRO_PLAY_PATH then
    macro_play_rows = {}
    local f = io.open(MACRO_PLAY_PATH, "r")
    if f then
        for line in f:lines() do
            local frame_number, mask = line:match("^(%d+) (%x+)$")
            if mask then
                macro_play_rows[#macro_play_rows + 1] = {
                    frame = tonumber(frame_number), mask = tonumber(mask, 16)
                }
            end
        end
        f:close()
    end
    log(string.format("macro: playback %d rows from %s timing=%s", #macro_play_rows,
        MACRO_PLAY_PATH, macro_play_preserve and "preserved" or "compressed"))
end

-- A save state restores the Lua VM too.  Re-arm macro playback after an
-- in-session checkpoint load so the input tail is applied to the restored
-- fight rather than the pre-load boot state.
if LOAD_STATE and MACRO_PLAY_PATH then
    emu.add_machine_post_load_notifier(function()
        macro_play_rows, macro_play_idx, macro_play_done = {}, 1, false
        macro_handles = nil
        macro_play_frame_offset = tonumber(os.getenv("VON_RECORD_MACRO_PLAY_FRAME_OFFSET") or "0") or 0
        macro_play_preserve = os.getenv("VON_RECORD_MACRO_PLAY_PRESERVE_TIMING") == "1"
        local f = io.open(MACRO_PLAY_PATH, "r")
        if f then
            for line in f:lines() do
                local frame_number, mask = line:match("^(%d+) (%x+)$")
                if mask then
                    macro_play_rows[#macro_play_rows + 1] = {
                        frame = tonumber(frame_number), mask = tonumber(mask, 16)
                    }
                end
            end
            f:close()
        end
        log(string.format("macro: rearmed after state load (%d rows)", #macro_play_rows))
        LOAD_STATE_DONE = true
        install_watches()
        install_struct_field_watch()
    end)
end

local function step_playback()
    if macro_play_done or not macro_play_rows then return end
    if macro_play_idx > #macro_play_rows then
        for _, h in ipairs(resolve_macro_fields()) do
            if h.field then pcall(function() set_pressed(h.field, false) end) end
        end
        macro_play_done = true
        log(string.format("macro f%d playback complete", frame))
        return
    end
    local playback_frame = frame + macro_play_frame_offset
    local row = macro_play_rows[macro_play_idx]
    if macro_play_preserve then
        if playback_frame < row.frame then
            row = nil
        else
            while macro_play_idx <= #macro_play_rows
                and macro_play_rows[macro_play_idx].frame < playback_frame do
                macro_play_idx = macro_play_idx + 1
            end
            if macro_play_idx > #macro_play_rows then
                row = nil
            elseif macro_play_rows[macro_play_idx].frame == playback_frame then
                row = macro_play_rows[macro_play_idx]
            else
                row = nil
            end
        end
    end
    local m = row and row.mask or 0
    if MACRO_PLAY_CLEAR_MASK ~= 0 then
        m = m & (~MACRO_PLAY_CLEAR_MASK)
    end
    if MACRO_PLAY_FORCE_MASK ~= 0 then
        m = m | MACRO_PLAY_FORCE_MASK
    end
    for i, h in ipairs(resolve_macro_fields()) do
        if not macro_play_logged_fields then
            log(string.format("macro: field%d mask=%s def=%s", i,
                tostring(h.mask), tostring(h.def)))
        end
        if h.field then
            local pressed = (m & (1 << (i - 1))) ~= 0
            pcall(function() set_pressed(h.field, pressed) end)
        end
    end
    macro_play_logged_fields = true
    if MACRO_PLAY_LOG_FROM >= 0 and frame >= MACRO_PLAY_LOG_FROM
        and frame <= MACRO_PLAY_LOG_TO then
        log(string.format("macroplay f%d row=%s mask=%04x read=%04x", frame,
            row and tostring(row.frame) or "none", m, read_mask()))
    end
    if not macro_play_preserve or row then macro_play_idx = macro_play_idx + 1 end
end

local shot_probe_field, shot_probe_port
local function step_shot_probe()
    if not SHOT_PROBE_FORCE_OFF and (SHOT_PROBE_FROM < 0
        or SHOT_PROBE_TO < SHOT_PROBE_FROM or SHOT_PROBE_INTERVAL <= 0) then return end
    if not shot_probe_field then
        shot_probe_field = resolve_bootstrap_field({ port = ":IN1", name = "P1 Left Shot" })
        shot_probe_port = manager.machine.ioport.ports[":IN1"]
    end
    if not shot_probe_field then return end
    local active = not SHOT_PROBE_FORCE_OFF
        and frame >= SHOT_PROBE_FROM and frame <= SHOT_PROBE_TO
    if active then
        local phase = (frame - SHOT_PROBE_FROM) % SHOT_PROBE_INTERVAL
        active = phase < SHOT_PROBE_HOLD
    end
    pcall(function() set_pressed(shot_probe_field, active) end)
    if SHOT_PROBE_FORCE_OFF or (frame >= SHOT_PROBE_FROM and frame <= SHOT_PROBE_TO) then
        local ok, pv = pcall(function() return shot_probe_port:read() end)
        log(string.format("shotprobe f%d pressed=%d read=%s", frame, active and 1 or 0,
            ok and string.format("%04x", pv) or "?"))
    end
end

-- Overlay: red REC circle while macro capture is active, plus a brief
-- white dot on every marker tap so taps are visible even when idle.
-- No circle primitive exists, so stroke one with line segments (ARGB).
local REC_RED = 0xffff0000
local TAP_WHITE = 0xffffffff
local function draw_overlay()
    if not macro_active and mark_flash <= 0 then return end
    pcall(function()
        local ui = manager.machine.render.ui_container
        if not ui then return end
        if macro_active then
            local cx, cy, r, n = 0.045, 0.06, 0.022, 16
            local px, py = cx + r, cy
            for i = 1, n do
                local a = (i / n) * math.pi * 2
                local qx, qy = cx + r * math.cos(a), cy + r * math.sin(a)
                ui:draw_line(px, py, qx, qy, REC_RED)
                px, py = qx, qy
            end
            ui:draw_text(0.075, 0.042, "REC", REC_RED)
        end
        if mark_flash > 0 then
            ui:draw_box(0.045, 0.10, 0.055, 0.115, TAP_WHITE, TAP_WHITE)
        end
    end)
end

local function install_recorder_callbacks()
emu.register_frame_done(function()
    -- Auto-start capture (also exercises the overlay headless).
    if MACRO_START and space and not macro_active and not macro_start_done then
        macro_start_done = true
        toggle_macro()
    end
    if mark_flash > 0 then mark_flash = mark_flash - 1 end
    draw_overlay()
end)

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            cpu_dev = cpu
            space = cpu.spaces[":program"] or cpu.spaces["program"]
        end
        if space and MARKER_PORT then
            local port = manager.machine.ioport.ports[MARKER_PORT]
            if port then
                marker_port = port
                marker = port.fields[MARKER_NAME]
                -- Cache the field bit and its inactive level: live state
                -- comes from port:read(), and pressed means the bit
                -- differs from its default (VON ports are active-low).
                if marker then
                    local ok, m = pcall(function() return marker.mask end)
                    if ok and type(m) == "number" then marker_mask = m end
                    local okd, d = pcall(function() return marker.defvalue end)
                    if okd and type(d) == "number" then marker_def = d end
                end
            end
        end
    if space then
            log("record: session start (passive, no inputs driven)")
            if marker then
                log(string.format("record: marker resolved %s:%s", MARKER_PORT, MARKER_NAME))
            else
                log(string.format("record: WARNING marker field missing %s:%s (no marks will log)",
                    tostring(MARKER_PORT), tostring(MARKER_NAME)))
            end
            install_watches()
            install_struct_field_watch()
        end
        return
    end
    sample_player_fields()
    if LOAD_STATE and not LOAD_STATE_DONE and frame <= 2 then
        LOAD_STATE_DONE = true
        log(string.format("record: scheduling state load f%d %s", frame, LOAD_STATE))
        pcall(function() manager.machine:load(LOAD_STATE) end)
    end
    step_bootstrap()
    if EXIT_FRAME > 0 and frame >= EXIT_FRAME then
        if macro_file then macro_file:close() macro_file = nil end
        snapshot("session-end")
        watch_summary("final")
        log(string.format("record: session complete (%d marks)", mark_count))
        manager.machine:exit()
        return
    end
    for _, spec in ipairs(STATELOGS) do
        if spec.every > 0 and frame % spec.every == 0 then
            statelog(spec)
        end
    end
    weapon_log()
    if SNAP_EVERY > 0 and frame % (SNAP_EVERY * 60) == 0 then
        snapshot(string.format("t%06ds", math.floor(frame / 60)))
    end
    if marker_port and marker_mask and marker_def then
        local ok, pv = pcall(function() return marker_port:read() end)
        local v = (ok and type(pv) == "number"
            and (pv & marker_mask) ~= (marker_def & marker_mask)) and 1 or 0
        if v == 1 and marker_last == 0 then
            mark_count = mark_count + 1
            log(string.format("mark f%d #%d", frame, mark_count))
            mark_flash = 15
            edge_times[#edge_times + 1] = frame
            if #edge_times > 3 then table.remove(edge_times, 1) end
            if #edge_times == 3 and edge_times[3] - edge_times[1] <= TRIPLE_WINDOW then
                edge_times = {}
                hold_toggled = true -- ongoing hold must not immediately re-toggle
                toggle_macro()
            end
        end
        -- Macro record hotkey: holding the marker key past MACRO_HOLD_FRAMES
        -- toggles capture once per press (the press itself still marks).
        if v == 1 then
            hold_frames = hold_frames + 1
            if hold_frames >= MACRO_HOLD_FRAMES and not hold_toggled then
                hold_toggled = true
                toggle_macro()
            end
        else
            hold_frames = 0
            hold_toggled = false
        end
        marker_last = v
    end
    if macro_active and macro_file then
        macro_file:write(string.format("%d %04x\n", frame, read_mask()))
    end
    if macro_play_rows then step_playback() end
    step_shot_probe()
    if SAVE_STATE_FRAME >= 0 and frame == SAVE_STATE_FRAME and not save_state_done then
        save_state_done = true
        log(string.format("record: scheduling state save f%d %s", frame, SAVE_STATE_NAME))
        pcall(function() manager.machine:save(SAVE_STATE_NAME) end)
    end
    if frame % 600 == 0 then watch_summary(string.format("f%d", frame)) end
    if frame % 60 == 0 then
        local h = screen_hash()
        if h and h ~= last_screen_hash then
            last_screen_hash = h
            log(string.format("record: frame %d screen %08x", frame, h))
        end
    end
end)
end

if DEFER_AFTER_STATE and LOAD_STATE then
    log("record: WARNING VON_RECORD_DEFER_AFTER_STATE with VON_RECORD_LOAD_STATE: " ..
        "deferred callbacks never install, so the scheduled load never fires; " ..
        "drive the load externally (e.g. MCP stateload) instead")
end
if DEFER_AFTER_STATE then
    emu.add_machine_post_load_notifier(install_recorder_callbacks)
else
    install_recorder_callbacks()
end
