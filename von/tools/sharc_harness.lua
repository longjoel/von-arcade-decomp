-- SHARC isolated-handler harness (Virtual-On, MAME vonj driver).
--
-- Injects COP FIFO packets straight into the live SHARC dispatcher and
-- records per-opcode observables WITHOUT touching SHARC firmware or the
-- MAME build: pre/post data-memory snapshots, per-frame program-counter
-- histogram, idle-loop return, and FIFO-block detection.
--
-- Protocol (see von/i960/disassembly-annotations.md, SHARC Service
-- Dispatcher): each u32 store to i960 program space 0x00884000 queues one
-- FIFO word and raises FLAG0_IN. The dispatcher (PM 0x20128-0x2012e) reads
-- one word as the opcode, indirect-calls DM(0x30000+opcode), and parks at
-- PM 0x20129 while idle. Opcode 0x08 re-initializes service state, so a
-- packet is usually {0x08, opcode, args...}.
--
-- Environment:
--   VON_SHARC_OPCODES      ";"-separated trials, each "op[:arg,arg...]"
--                          in hex; the opcode word is queued first, then
--                          the args, e.g. "08;00:3f800000,40000000" runs
--                          init (08) then add (00) with 1.0, 2.0
--                          (default "00:"). Opcode fe is a no-inject
--                          baseline window: same snapshots, no FIFO words.
--                          Opcode fd drains N output-FIFO words host-side
--                          (first arg, default 4) to prove a handler ran.
--   VON_SHARC_SETTLE_FRAMES frames to wait for boot+park (default 400)
--   VON_SHARC_WINDOW_END last frame new trials may start: the SHARC
--                          sits idle from ~frame 300 to ~frame 1160, then
--                          attract geometry begins (default 1100)
--   VON_SHARC_RUN_FRAMES    max observe frames per trial (default 600)
--   VON_SHARC_STILL_FRAMES  same-PC frames that count as blocked (default 30)
--   VON_SHARC_DM_WINDOWS    "base:len,..." hex snapshot windows
--                          (default "30000:400,0:100")
--   VON_SHARC_POKES        "addr=val,..." hex DM fixtures, written after
--                          the pre-snapshot in EVERY run (injected and
--                          baseline alike) so subtraction stays valid
--   VON_SHARC_LOG          JSONL output path (required)
--
-- One JSON object per line: {type="trial", ...} and a final {type="done"}.
-- Frame numbers are attract-timing dependent; compare write_sets and
-- pc_ranges across runs, never exact frames.

local IDLE_PC = 0x20129
local FIFO_ADDR = 0x00884000

local function getenv_num(name, default)
    local raw = os.getenv(name)
    if raw == nil or raw == "" then return default end
    return tonumber(raw) or default
end

local SETTLE_FRAMES = getenv_num("VON_SHARC_SETTLE_FRAMES", 400)
local WINDOW_END = getenv_num("VON_SHARC_WINDOW_END", 1100)
local RUN_FRAMES = getenv_num("VON_SHARC_RUN_FRAMES", 600)
local STILL_FRAMES = getenv_num("VON_SHARC_STILL_FRAMES", 30)
local LOG_PATH = os.getenv("VON_SHARC_LOG")

local function parse_spec(text)
    local trials = {}
    for item in string.gmatch((text or "00:") .. ";", "([^;]+);") do
        local op, words = string.match(item, "^([^:]+):?(.*)$")
        local trial = { opcode = tonumber(op, 16), words = {} }
        if words and words ~= "" then
            for w in string.gmatch(words, "([^,]+)") do
                trial.words[#trial.words + 1] = tonumber(w, 16)
            end
        end
        trials[#trials + 1] = trial
    end
    return trials
end

local TRIALS = parse_spec(os.getenv("VON_SHARC_OPCODES") or "00:")

local function parse_windows(text)
    local windows = {}
    for item in string.gmatch(text or "30000:400,0:100", "([^,]+)") do
        local base, len = string.match(item, "^([^:]+):([^:]+)$")
        windows[#windows + 1] = { base = tonumber(base, 16), len = tonumber(len, 16) }
    end
    return windows
end

local WINDOWS = parse_windows(os.getenv("VON_SHARC_DM_WINDOWS"))

local function parse_pokes(text)
    local pokes = {}
    if text and text ~= "" then
        for item in string.gmatch(text .. ",", "([^,]+),") do
            local addr, val = string.match(item, "^([^=]+)=([^=]+)$")
            if addr and val then
                pokes[#pokes + 1] = { addr = tonumber(addr, 16),
                    val = tonumber(val, 16) }
            end
        end
    end
    return pokes
end

local POKES = parse_pokes(os.getenv("VON_SHARC_POKES"))

local log_file = nil
local main_space = nil
local sharc_data = nil
local sharc = nil
local frame = 0
local phase = "settle" -- settle | inject | observe | finish
local trial_index = 0
local trial = nil
local trial_frame = 0
local inject_wait = 0
local pc_hist = {}
local last_pc = nil
local still = 0
local idle_return_frame = nil
local snapshot = nil

local function log_json(obj)
    if not log_file then return end
    local parts = {}
    for k, v in pairs(obj) do parts[#parts + 1] = k .. "=" .. tostring(v) end
    -- Minimal flat JSON: values are numbers, strings (no quotes inside), or
    -- pre-encoded fragments under keys ending in "_json".
    local out = {}
    for k, v in pairs(obj) do
        if string.sub(k, -5) == "_json" then
            out[#out + 1] = string.format('"%s":%s', string.sub(k, 1, -6), v)
        elseif type(v) == "number" then
            out[#out + 1] = string.format('"%s":%d', k, v)
        else
            out[#out + 1] = string.format('"%s":"%s"', k, tostring(v))
        end
    end
    log_file:write("{" .. table.concat(out, ",") .. "}\n")
    log_file:flush()
end

local function read_pc()
    local ok, pc = pcall(function() return sharc.state["PC"].value end)
    if ok then return pc end
    return nil
end

local function take_snapshot()
    local snap = {}
    for _, w in ipairs(WINDOWS) do
        local words = {}
        for i = 0, w.len - 1 do
            local ok, val = pcall(function()
                return sharc_data:read_u32(w.base + i)
            end)
            words[#words + 1] = ok and string.format("%08x", val) or "????????"
        end
        snap[#snap + 1] = string.format("%05x:%s", w.base, table.concat(words, ""))
    end
    return snap
end

local function diff_snapshots(before, after)
    local diffs = {}
    for wi, w in ipairs(WINDOWS) do
        local b = string.sub(before[wi], 7)
        local a = string.sub(after[wi], 7)
        for i = 0, w.len - 1 do
            local bo = string.sub(b, i * 8 + 1, i * 8 + 8)
            local ao = string.sub(a, i * 8 + 1, i * 8 + 8)
            if bo ~= ao then
                diffs[#diffs + 1] = string.format("%05x:%s->%s",
                    w.base + i, bo, ao)
            end
        end
    end
    return diffs
end

local function start_trial(t)
    trial = t
    trial_frame = 0
    pc_hist = {}
    last_pc = nil
    still = 0
    idle_return_frame = nil
    trial.drain = nil
    snapshot = take_snapshot()
    for _, poke in ipairs(POKES) do
        pcall(function() sharc_data:write_u32(poke.addr, poke.val) end)
    end
    if t.opcode == 0xFD then
        local n = t.words[1] or 4
        local vals = {}
        for i = 1, n do
            local ok, val = pcall(function()
                return main_space:read_u32(FIFO_ADDR)
            end)
            vals[#vals + 1] = ok and string.format("%08x", val) or "????????"
        end
        trial.drain = vals
    elseif t.opcode ~= 0xFE then
        main_space:write_u32(FIFO_ADDR, t.opcode)
    end
    if t.opcode ~= 0xFD then
        for _, word in ipairs(t.words) do
            main_space:write_u32(FIFO_ADDR, word)
        end
    end
    phase = "observe"
end

local function finish_trial(outcome)
    local after = take_snapshot()
    local diffs = diff_snapshots(snapshot, after)
    local post = {}
    for _, s in ipairs(after) do post[#post + 1] = '"' .. s .. '"' end
    local ranges = {}
    for pc, count in pairs(pc_hist) do
        ranges[#ranges + 1] = string.format("%06x*%d", pc, count)
    end
    table.sort(ranges)
    local words = {}
    for _, w in ipairs(trial.words) do words[#words + 1] = string.format("%08x", w) end
    local drainfrag = '"nodrain"'
    if trial.drain then
        drainfrag = '["' .. table.concat(trial.drain, '","') .. '"]'
    end
    log_json({
        type = "trial",
        opcode = string.format("%02x", trial.opcode),
        words_json = '["' .. table.concat(words, '","') .. '"]',
        outcome = outcome,
        observe_frames = trial_frame,
        idle_return_frame = idle_return_frame or -1,
        write_count = #diffs,
        writes_json = '["' .. table.concat(diffs, '","') .. '"]',
        pc_ranges_json = '["' .. table.concat(ranges, '","') .. '"]',
        post_json = '[' .. table.concat(post, ',') .. ']',
        drain_json = drainfrag,
    })
    trial = nil
    trial_index = trial_index + 1
    if trial_index > #TRIALS then
        phase = "finish"
    else
        phase = "inject"
    end
end

emu.register_frame_done(function()
    frame = frame + 1
    if not main_space then
        local cpu = manager.machine.devices[":maincpu"]
        sharc = manager.machine.devices[":copro_adsp"]
        if cpu and sharc then
            main_space = cpu.spaces["program"] or cpu.spaces[":program"]
            local spaces = sharc.spaces
            sharc_data = spaces["data"] or spaces[":data"]
            if not LOG_PATH then
                manager.machine:exit()
                return
            end
            log_file = assert(io.open(LOG_PATH, "w"))
            log_json({ type = "start", settle_frames = SETTLE_FRAMES,
                run_frames = RUN_FRAMES })
        end
        return
    end
    if phase == "settle" then
        if frame >= SETTLE_FRAMES then
            local pc = read_pc()
            if pc == IDLE_PC then
                trial_index = 1
                phase = "inject"
            elseif frame >= SETTLE_FRAMES + 600 then
                log_json({ type = "abort", reason = "never-parked",
                    last_pc = pc or -1 })
                phase = "finish"
            end
        end
    elseif phase == "inject" then
        if frame > WINDOW_END then
            log_json({ type = "abort", reason = "window-closed",
                completed = trial_index - 1, total = #TRIALS })
            phase = "finish"
            return
        end
        local pc = read_pc()
        if pc == IDLE_PC then
            inject_wait = 0
            start_trial(TRIALS[trial_index])
        else
            inject_wait = inject_wait + 1
        end
        if frame >= SETTLE_FRAMES + 1200 then
            log_json({ type = "abort", reason = "inject-never-idle" })
            phase = "finish"
        end
    elseif phase == "observe" then
        trial_frame = trial_frame + 1
        local pc = read_pc()
        if pc then
            pc_hist[pc] = (pc_hist[pc] or 0) + 1
            if pc == last_pc then
                still = still + 1
            else
                still = 0
                last_pc = pc
            end
            if pc == IDLE_PC and trial_frame > 2 and not idle_return_frame then
                idle_return_frame = trial_frame
            end
        end
        if idle_return_frame and trial_frame >= idle_return_frame + 5 then
            finish_trial("returned")
        elseif still >= STILL_FRAMES and last_pc ~= IDLE_PC then
            finish_trial(string.format("blocked-%06x", last_pc or 0))
        elseif trial_frame >= RUN_FRAMES then
            finish_trial("timeout")
        end
    elseif phase == "finish" then
        log_json({ type = "done", frames = frame })
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
