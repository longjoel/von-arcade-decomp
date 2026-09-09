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
--   VON_WATCH_WRITES        "base,len[;...]" write-watch windows for writer
--                           PC capture (default off). Each window gets a
--                           passive write tap; distinct writer PCs per
--                           window are counted and summarized as watch:
--                           lines every 600 frames and at session end.
--                           Example: VON_WATCH_WRITES="0x503CB8,0x4"
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

local log_file = assert(io.open(LOG_PATH, "w"))
local function log(message)
    log_file:write(message .. "\n")
    log_file:flush()
end

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

local hold_frames, hold_toggled = 0, false
local macro_active, macro_file, macro_handles = false, nil, nil
local macro_start_done = false
-- Triple-tap toggle: 3 rising edges within TRIPLE_WINDOW frames toggles too,
-- so a sticky/impulse/jittery field that never reads a sustained level can
-- still arm capture. Jump-apex taps are seconds apart and never qualify.
local TRIPLE_WINDOW = 40
local edge_times = {}
local mark_flash = 0
local macro_path = SNAP_DIR .. "/../macro.txt"
local macro_play_rows, macro_play_idx, macro_play_done = nil, 1, false

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
            local mask = line:match("^%d+ (%x+)$")
            if mask then macro_play_rows[#macro_play_rows + 1] = tonumber(mask, 16) end
        end
        f:close()
    end
    log(string.format("macro: playback %d rows from %s", #macro_play_rows, MACRO_PLAY_PATH))
end

local function step_playback()
    if macro_play_done or not macro_play_rows then return end
    if macro_play_idx > #macro_play_rows then
        for _, h in ipairs(resolve_macro_fields()) do
            if h.field then pcall(function() h.field:set_value(0) end) end
        end
        macro_play_done = true
        log(string.format("macro f%d playback complete", frame))
        return
    end
    local m = macro_play_rows[macro_play_idx]
    for i, h in ipairs(resolve_macro_fields()) do
        if h.field then
            local bit = (m & (1 << (i - 1))) ~= 0 and 1 or 0
            pcall(function() h.field:set_value(bit) end)
        end
    end
    macro_play_idx = macro_play_idx + 1
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
        end
        return
    end
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
    if frame % 600 == 0 then watch_summary(string.format("f%d", frame)) end
    if frame % 60 == 0 then
        local h = screen_hash()
        if h and h ~= last_screen_hash then
            last_screen_hash = h
            log(string.format("record: frame %d screen %08x", frame, h))
        end
    end
end)
