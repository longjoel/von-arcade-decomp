-- Battle input fuzzer with per-window RAM snapshots.
--
-- Warps through the scripted coin/select/start flow into the first battle,
-- then holds each P1 input in isolation and snapshots RAM before, during,
-- and after the hold. The pre/post/settled triple discriminates
-- input-driven fields from background churn.
--
-- P2 side: run the same flow with VON_FUZZ_IDLE=1 (joins versus, then sends
-- nothing), so the enemy is a human-controlled idle dummy: AI off.
--
-- Environment:
--   VON_FUZZ_LOG        log path
--   VON_FUZZ_SNAP_DIR   snapshot directory (files snap-<input>-<phase>.txt)
--   VON_FUZZ_COIN       coin frame (default 900)
--   VON_FUZZ_START      start frame (default 1500)
--   VON_FUZZ_BATTLE     first fuzz frame (default 2400)
--   VON_FUZZ_HOLD       hold frames per input (default 45)
--   VON_FUZZ_SETTLE     settle frames after release (default 45)
--   VON_FUZZ_IDLE       if 1, join but never drive combat inputs
--   VON_FUZZ_SECONDS    total seconds (default 150)
--
-- Snapshot regions (base/len): object table, transition cells, player
-- workspaces, and the low workram window where the input latch lives.
-- Format matches snap-*.txt ("%08x %08x") for diff compatibility.

local LOG_PATH = os.getenv("VON_FUZZ_LOG") or "vonj-fuzz.log"
local SNAP_DIR = os.getenv("VON_FUZZ_SNAP_DIR") or "vonj-fuzz-snaps"
local COIN_FRAME = tonumber(os.getenv("VON_FUZZ_COIN") or "900")
local START_FRAME = tonumber(os.getenv("VON_FUZZ_START") or "1500")
local START2_FRAME = tonumber(os.getenv("VON_FUZZ_START2") or "0")
local NO_START = os.getenv("VON_FUZZ_NO_START") == "1"
-- Single-cabinet 2P versus: a second credit (default off). Versus select
-- cursor: VON_FUZZ_SELECT_STEPS right-presses from the default, starting at
-- VON_FUZZ_SELECT_FRAME; confirmation is by timeout (auto-confirm).
local COIN2_FRAME = tonumber(os.getenv("VON_FUZZ_COIN2") or "0")
local SELECT_FRAME = tonumber(os.getenv("VON_FUZZ_SELECT_FRAME") or "0")
local SELECT_STEPS = tonumber(os.getenv("VON_FUZZ_SELECT_STEPS") or "0")
-- Row-2 picks: VON_FUZZ_SELECT_DOWN down-presses walk the cursor to the
-- second row first, then SELECT_STEPS right-presses run.
local SELECT_DOWN = tonumber(os.getenv("VON_FUZZ_SELECT_DOWN") or "0")
-- Force the game's link role: the comm firmware reads shared[1]
-- (0x01=master, 0x02=slave) with fallback to the fg bit. The service
-- menu normally sources this; forcing overrides whatever it holds.
local COMM_ROLE = tonumber(os.getenv("VON_FUZZ_COMM_ROLE") or "0")
local BATTLE_FRAME = tonumber(os.getenv("VON_FUZZ_BATTLE") or "2400")
-- Single-player flows park on character select after START; one extra START
-- press confirms the default pick. Versus flows auto-confirm (leave 0).
local CONFIRM_FRAME = tonumber(os.getenv("VON_FUZZ_CONFIRM") or "0")
local HOLD = tonumber(os.getenv("VON_FUZZ_HOLD") or "45")
local SETTLE = tonumber(os.getenv("VON_FUZZ_SETTLE") or "45")
local IDLE = os.getenv("VON_FUZZ_IDLE") == "1"
local SECONDS = tonumber(os.getenv("VON_FUZZ_SECONDS") or "150")

local REGIONS = {
    { 0x515000, 0x4000 },  -- 64 x 256B object slots
    { 0x504c80, 0x0400 },  -- transition cells
    { 0x5039c0, 0x0300 },  -- player workspaces
    { 0x500000, 0x6000 },  -- low workram (input latch hunt)
}

local INPUTS = {
    "up", "down", "left", "right",
    "r_up", "r_down", "r_left", "r_right",
    "left_shot", "right_shot", "left_dash", "right_dash",
    -- combos (plus-separated keys): both triggers = center weapon,
    -- outward sticks = jump, inward sticks = guard/crouch, dash+shot.
    "left_shot+right_shot", "left+r_right", "right+r_left", "up+r_up",
    "left_dash+left_shot", "right_dash+right_shot",
    "right+r_left+left_shot",
    -- true dashes need a direction held with the dash button.
    "up+left_dash", "left+left_dash", "up+right_dash",
}

-- Optional subset: VON_FUZZ_ONLY="left_dash,right_dash" runs just those.
do
    local only_raw = os.getenv("VON_FUZZ_ONLY")
    if only_raw and only_raw ~= "" then
        local want = {}
        for tok in string.gmatch(only_raw, "([^,]+)") do want[tok] = true end
        local sub = {}
        for _, key in ipairs(INPUTS) do
            if want[key] then sub[#sub + 1] = key end
        end
        if #sub > 0 then INPUTS = sub end
    end
end

local function split_keys(combo)
    local keys = {}
    for tok in string.gmatch(combo, "([^+]+)") do keys[#keys + 1] = tok end
    return keys
end

local function tag_of(combo)
    return (string.gsub(combo, "%+", "_"))
end

local FIELD_NAMES = {
    coin       = { ":IN0", "Coin 1" },
    start      = { ":IN0", "1 Player Start" },
    start2     = { ":IN0", "2 Players Start" },
    down       = { ":IN1", "P1 Left Stick/Down" },
    up         = { ":IN1", "P1 Left Stick/Up" },
    right      = { ":IN1", "P1 Left Stick/Right" },
    left       = { ":IN1", "P1 Left Stick/Left" },
    left_shot  = { ":IN1", "P1 Left Shot" },
    left_dash  = { ":IN1", "P1 Left Dash" },
    right_shot = { ":IN2", "P1 Right Shot" },
    right_dash = { ":IN2", "P1 Right Dash" },
    r_down     = { ":IN2", "P1 Right Stick/Down" },
    r_up       = { ":IN2", "P1 Right Stick/Up" },
    r_right    = { ":IN2", "P1 Right Stick/Right" },
    r_left     = { ":IN2", "P1 Right Stick/Left" },
}

local TILE_BASE = 0x01000000
local ROWS, COLS = 64, 64

local log_file = assert(io.open(LOG_PATH, "w"))
local function log(msg)
    log_file:write(msg .. "\n")
    log_file:flush()
end

local frame = 0
local space = nil
local cpu_dev = nil
local fields = {}

-- Read watchpoints on latched fields: which code reads them, and when.
-- VON_FUZZ_TAPS="0x5007f0,0x504d94" installs taps during each hold window
-- and logs distinct reader PCs per window on release.
local TAP_ADDRS = {}
do
    local raw = os.getenv("VON_FUZZ_TAPS") or ""
    for tok in string.gmatch(raw, "([^,]+)") do
        local addr = tonumber(tok)
        if addr then TAP_ADDRS[#TAP_ADDRS + 1] = addr end
    end
end
local active_taps = {}
local tap_pcs = {}

-- Per-frame telemetry during holds: VON_FUZZ_TELEMETRY="0x503a14,0x504d80"
-- logs one compact hex row per frame so motion arcs can be reconstructed
-- from RAM without the geometry trace build.
local TELEMETRY = {}
do
    local raw = os.getenv("VON_FUZZ_TELEMETRY") or ""
    for tok in string.gmatch(raw, "([^,]+)") do
        local addr = tonumber(tok)
        if addr then TELEMETRY[#TELEMETRY + 1] = addr end
    end
end

-- Battle-long state time series for the geometry join: VON_FUZZ_STATELOG
-- "base,len,every[;base,len,every...]" dumps one hex row per <every> frames
-- from BATTLE_FRAME to session end, so RAM state joins against annotation
-- pose_segments by timestamp (fuzz frame/60 = trace machine seconds).
-- Example: VON_FUZZ_STATELOG="0x504c80,0x400,2;0x5039c0,0x300,5" tracks the
-- transition cells every 2nd frame and the player workspaces at 12Hz.
local STATELOGS = {}
do
    local raw = os.getenv("VON_FUZZ_STATELOG") or ""
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

local function statelog(spec)
    if not space or not spec.base then return end
    local words = {}
    for addr = spec.base, spec.base + spec.len - 1, 4 do
        local ok, v = pcall(function() return space:read_u32(addr) end)
        words[#words + 1] = ok and string.format("%08x", v) or "????????"
    end
    log(string.format("fuzz: state f%d @%08x %s", frame, spec.base,
        table.concat(words, " ")))
end

local function telemetry(tag)
    if not space or #TELEMETRY == 0 then return end
    local words = {}
    for _, addr in ipairs(TELEMETRY) do
        local ok, v = pcall(function() return space:read_u32(addr) end)
        words[#words + 1] = ok and string.format("%08x", v) or "????????"
    end
    log(string.format("fuzz: tele %s f%d %s", tag, frame,
        table.concat(words, " ")))
end

local function install_taps()
    if not space or #TAP_ADDRS == 0 then return end
    for _, addr in ipairs(TAP_ADDRS) do
        tap_pcs[addr] = { _n = 0 }
        local ok, tap = pcall(function()
            return space:install_read_tap(addr, addr + 3,
                string.format("fuzz%08x", addr),
                function(offset, data, mask)
                    local seen = tap_pcs[addr]
                    if seen._n < 25 and cpu_dev then
                        local pc = "?"
                        local okc, st = pcall(function()
                            return cpu_dev.state["CURPC"].value
                        end)
                        if okc and type(st) == "number" then
                            pc = string.format("0x%x", st)
                        end
                        if not seen[pc] then
                            seen[pc] = 0
                            seen._n = seen._n + 1
                        end
                        seen[pc] = seen[pc] + 1
                    end
                    return data
                end)
        end)
        if ok and tap then active_taps[addr] = tap end
    end
end

local function remove_taps(tag)
    for addr, tap in pairs(active_taps) do
        pcall(function() space:uninstall_read_tap(tap) end)
        local pcs = {}
        for pc, n in pairs(tap_pcs[addr] or {}) do
            if pc ~= "_n" then
                pcs[#pcs + 1] = string.format("%s(x%d)", pc, n)
            end
        end
        table.sort(pcs)
        log(string.format("fuzz: tap %08x %s readers=%d %s",
            addr, tag, #pcs, table.concat(pcs, " ")))
    end
    active_taps = {}
    tap_pcs = {}
end
local fuzz_index = 0
local fuzz_phase = "idle"  -- idle | hold | settle
local fuzz_frame = 0
local last_screen_hash = nil

local function snapshot(tag)
    for _, region in ipairs(REGIONS) do
        local base, len = region[1], region[2]
        local path = string.format("%s/snap-%s-%04x.txt", SNAP_DIR, tag, base)
        local out = assert(io.open(path, "w"))
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
    local hash = 2166136261
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

local function screen_text()
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

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            cpu_dev = cpu
            space = cpu.spaces[":program"] or cpu.spaces["program"]
        end
        if space then
            for key, spec in pairs(FIELD_NAMES) do
                local port = manager.machine.ioport.ports[spec[1]]
                fields[key] = port and port.fields[spec[2]] or nil
            end
            log("fuzz: fields resolved")
        else
            return
        end
    end
    if not fields.coin then return end

    if frame == COIN_FRAME then
        fields.coin:set_value(1)
        log("fuzz: coin")
    elseif frame == COIN_FRAME + 8 then
        fields.coin:clear_value()
    elseif COIN2_FRAME > 0 and frame == COIN2_FRAME then
        fields.coin:set_value(1)
        log("fuzz: coin2")
    elseif COIN2_FRAME > 0 and frame == COIN2_FRAME + 8 then
        fields.coin:clear_value()
    elseif frame == START_FRAME and not NO_START then
        fields.start:set_value(1)
        log("fuzz: start")
    elseif frame == START_FRAME + 8 and not NO_START then
        fields.start:clear_value()
    elseif CONFIRM_FRAME > 0 and frame == CONFIRM_FRAME then
        fields.start:set_value(1)
        log("fuzz: confirm")
    elseif CONFIRM_FRAME > 0 and frame == CONFIRM_FRAME + 8 then
        fields.start:clear_value()
    elseif START2_FRAME > 0 and frame == START2_FRAME then
        if fields.start2 then
            fields.start2:set_value(1)
            log("fuzz: start2 (versus join)")
        end
    elseif START2_FRAME > 0 and frame == START2_FRAME + 8 then
        if fields.start2 then fields.start2:clear_value() end
    end

    -- Versus select cursor walk: SELECT_DOWN down-presses (row 2) first,
    -- then one 6-frame right-press per 36-frame slot.
    if SELECT_FRAME > 0 and fields.right and fields.down then
        local total = SELECT_DOWN + SELECT_STEPS
        local rel = frame - SELECT_FRAME
        if rel >= 0 then
            local slot = math.floor(rel / 36)
            local ph = rel % 36
            if slot < total then
                local key = (slot < SELECT_DOWN) and "down" or "right"
                local n = (slot < SELECT_DOWN) and (slot + 1) or (slot - SELECT_DOWN + 1)
                if ph == 0 then
                    fields[key]:set_value(1)
                    log(string.format("fuzz: select %s %d", key, n))
                elseif ph == 6 then
                    fields[key]:clear_value()
                end
            elseif slot == total and ph == 0 then
                fields.right:clear_value()
                fields.down:clear_value()
            end
        end
    end

    if frame == BATTLE_FRAME then
        snapshot("battle-entry")
    end

    if frame >= BATTLE_FRAME then
        for _, spec in ipairs(STATELOGS) do
            if spec.every > 0 and frame % spec.every == 0 then
                statelog(spec)
            end
        end
    end

    -- Snapshot schedule runs on both sides (framesync keeps P1/P2 in
    -- lockstep); only the non-idle side drives inputs.
    if frame >= BATTLE_FRAME and fuzz_index <= #INPUTS then
        fuzz_frame = fuzz_frame + 1
        if fuzz_phase == "idle" then
            fuzz_index = fuzz_index + 1
            if fuzz_index > #INPUTS then
                snapshot("fuzz-done")
            else
                local combo = INPUTS[fuzz_index]
                local tag = tag_of(combo)
                snapshot(tag .. "-pre")
                if not IDLE then
                    for _, key in ipairs(split_keys(combo)) do
                        if fields[key] then fields[key]:set_value(1) end
                    end
                    log(string.format("fuzz: frame %d hold %s", frame, combo))
                end
                install_taps()
                telemetry(tag_of(combo) .. "-begin")
                fuzz_phase = "hold"
                fuzz_frame = 0
            end
        elseif fuzz_phase == "hold" then
            if #TELEMETRY > 0 and fuzz_frame % 5 == 0 then
                telemetry(tag_of(INPUTS[fuzz_index]))
            end
        end
        if fuzz_phase == "hold" and fuzz_frame >= HOLD then
            local combo = INPUTS[fuzz_index]
            local tag = tag_of(combo)
            snapshot(tag .. "-post")
            remove_taps(tag)
            if not IDLE then
                for _, key in ipairs(split_keys(combo)) do
                    if fields[key] then fields[key]:clear_value() end
                end
                log(string.format("fuzz: frame %d release %s", frame, combo))
            end
            fuzz_phase = "settle"
            fuzz_frame = 0
        elseif fuzz_phase == "settle" and fuzz_frame >= SETTLE then
            snapshot(tag_of(INPUTS[fuzz_index]) .. "-settled")
            fuzz_phase = "idle"
            fuzz_frame = 0
        end
    end

    if frame % 30 == 0 then
        local h = screen_hash()
        if h and h ~= last_screen_hash then
            last_screen_hash = h
            local ok, text = pcall(screen_text)
            if ok and text:match("%S") then
                log(string.format("fuzz: frame %d screen %08x TEXT >>>\n%s\n<<< END",
                    frame, h, text))
            else
                log(string.format("fuzz: frame %d screen %08x (graphics)", frame, h))
            end
        end
    end

    if COMM_ROLE > 0 and frame % 30 == 0 and space then
        pcall(function() space:write_u8(0x1a00001, COMM_ROLE) end)
    end

    if frame >= SECONDS * 60 then
        log("fuzz: session complete")
        manager.machine:exit()
    end
end)
