-- Deterministic action schedule + the ordered i960/SHARC transform stream.
--
-- This is action_schedule.lua (same CYCLE/inputs) plus the transform taps from
-- gameplay_progress.lua (i960 FIFO packet words, SHARC stack push/pop bases,
-- and the 13-word geometry commit).  It exists so the match idle/jump windows
-- produce joined push/commit programs for the player traversal, which the
-- passive gameplay_progress schedule does not drive.
--
-- Env: VON_ACTION_LOG (required), VON_ACTION_TRANSFORM_LOG (optional NDJSON),
--      VON_ACTION_SECONDS (default 40), VON_ACTION_START_FRAME (default 2120),
--      VON_ACTION_CYCLES (default 2).

local LOG_PATH = assert(os.getenv("VON_ACTION_LOG"), "VON_ACTION_LOG required")
local TRANSFORM_PATH = os.getenv("VON_ACTION_TRANSFORM_LOG")
local SECONDS = tonumber(os.getenv("VON_ACTION_SECONDS") or "40")
local START_FRAME = tonumber(os.getenv("VON_ACTION_START_FRAME") or "2120")
local CYCLES = tonumber(os.getenv("VON_ACTION_CYCLES") or "2")
local COIN_FRAME = tonumber(os.getenv("VON_PROGRESS_COIN_FRAME") or "900")
local MATCH_START = tonumber(os.getenv("VON_PROGRESS_START_FRAME") or "1500")
local SELECT_STEPS = tonumber(os.getenv("VON_ACTION_SELECT_STEPS") or "0")
local SELECT_SETTLE = 180
local SELECT_STEP_FRAMES = 45

local log_file = assert(io.open(LOG_PATH, "w"))
log_file:write("action: session start\n")
log_file:flush()

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

-- Ordered transform stream -------------------------------------------------
local transform_file
local transform_event_id = 0
local sharc_device
local sharc_space
local sharc_commit_tap
local sharc_stack_tap
local sharc_reading = false
local sharc_last_depth = 0
local sharc_pending_stack_kind
local i960_fifo_tap
local commit_run = { start = nil, next = nil, words = {} }

local function transform_event(kind, body)
    if not transform_file then return end
    transform_event_id = transform_event_id + 1
    transform_file:write(string.format(
        '{"event_id":%d,"kind":"%s","frame":%d%s}\n',
        transform_event_id, kind, frame, body or ""))
    transform_file:flush()
end

local function state_value(device, name)
    local entry = device and device.state and device.state[name]
    return entry and tonumber(entry.value) or 0
end

local function matrix_at(address)
    local words = {}
    for i = 0, 11 do
        local ok, word = pcall(function()
            return sharc_space:read_u32(address + i)
        end)
        words[#words + 1] = ok and word or 0xffffffff
    end
    return words
end

local function json_words(words)
    local out = {}
    for _, word in ipairs(words) do out[#out + 1] = tostring(word) end
    return "[" .. table.concat(out, ",") .. "]"
end

local function flush_commit_run()
    if #commit_run.words == 13 and commit_run.words[1] == 0x05800b0b then
        local matrix = {}
        for i = 2, 13 do matrix[#matrix + 1] = commit_run.words[i] end
        transform_event("commit", string.format(
            ',"pc":%d,"depth":%d,"destination":"0x%08x",' ..
            '"matrix_words":%s,"stack_words":%s',
            state_value(sharc_device, "CURPC"), sharc_last_depth,
            commit_run.start, json_words(matrix),
            json_words(commit_run.stack_words or {})))
    elseif #commit_run.words > 0 then
        transform_event("commit_fragment", string.format(
            ',"destination":"0x%08x","word_count":%d',
            commit_run.start, #commit_run.words))
    end
    commit_run = { start = nil, next = nil, words = {} }
end

local function log(msg)
    log_file:write(msg .. "\n")
    log_file:flush()
end

local function now()
    local ok, t = pcall(function() return manager.machine.time:as_double() end)
    if ok and type(t) == "number" then return t end
    return frame / 60.0
end

local function find_sharc()
    for _, dev in pairs(manager.machine.devices) do
        if dev.shortname == "adsp21062" then return dev end
    end
    return manager.machine.devices[":copro"]
end

local function install_transform_taps()
    if not transform_file or not space then return end
    if not i960_fifo_tap then
        i960_fifo_tap = space:install_write_tap(
            0x00884000, 0x00884003, "von-action-transform-fifo",
            function(offset, data, mask)
                transform_event("i960_fifo", string.format(
                    ',"pc":%d,"data":%d,"mask":%d,"r6":%d,"g0":%d,"g2":%d,"g4":%d',
                    state_value(manager.machine.devices[":maincpu"], "CURPC"),
                    data, mask,
                    state_value(manager.machine.devices[":maincpu"], "r6"),
                    state_value(manager.machine.devices[":maincpu"], "g0"),
                    state_value(manager.machine.devices[":maincpu"], "g2"),
                    state_value(manager.machine.devices[":maincpu"], "g4")))
                return data
            end)
    end
    if sharc_commit_tap then return end
    sharc_device = find_sharc()
    if not sharc_device then return end
    sharc_space = sharc_device.spaces[":data"] or sharc_device.spaces["data"]
        or sharc_device.spaces[":program"] or sharc_device.spaces["program"]
    if not sharc_space then return end
    pcall(function()
        sharc_commit_tap = sharc_space:install_write_tap(
            0x01400000, 0x01410000, "von-action-sharc-commit",
            function(offset, data, mask)
                if sharc_reading then return data end
                sharc_reading = true
                if commit_run.start == nil then
                    commit_run.start = offset
                    commit_run.next = offset
                    local ptr_ok, ptr = pcall(function()
                        return sharc_space:read_u32(0x0030101)
                    end)
                    if ptr_ok then commit_run.stack_words = matrix_at(ptr) end
                elseif offset ~= commit_run.next then
                    flush_commit_run()
                    commit_run.start = offset
                    commit_run.next = offset
                end
                commit_run.words[#commit_run.words + 1] = data
                commit_run.next = offset + 1
                if #commit_run.words == 13 then flush_commit_run() end
                sharc_reading = false
                return data
            end)
    end)
    pcall(function()
        sharc_stack_tap = sharc_space:install_write_tap(
            0x0030100, 0x0030260, "von-action-sharc-stack",
            function(offset, data, mask)
                if sharc_reading then return data end
                sharc_reading = true
                local pc = state_value(sharc_device, "CURPC")
                if offset == 0x0030100 then
                    if data > sharc_last_depth then
                        sharc_pending_stack_kind = "push"
                    elseif data < sharc_last_depth then
                        sharc_pending_stack_kind = "pop"
                    else
                        sharc_pending_stack_kind = "reset"
                    end
                    sharc_last_depth = data
                elseif offset == 0x0030101 then
                    local words = matrix_at(data)
                    local kind = sharc_pending_stack_kind or "stack_pointer"
                    local depth = sharc_last_depth
                    local field, suffix = "matrix_words", ""
                    if kind == "push" then
                        field = "base_words"
                    elseif kind == "pop" then
                        depth = sharc_last_depth + 1
                        field = "restored_words"
                        suffix = string.format(',"depth_after":%d', sharc_last_depth)
                    end
                    transform_event(kind, string.format(
                        ',"pc":%d,"depth":%d%s,"pointer":%d,"%s":%s',
                        pc, depth, suffix, data, field, json_words(words)))
                    sharc_pending_stack_kind = nil
                end
                sharc_reading = false
                return data
            end)
    end)
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
    if TRANSFORM_PATH and not transform_file then
        transform_file = assert(io.open(TRANSFORM_PATH, "w"))
        transform_file:flush()
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
        if SELECT_STEPS <= 0 then
            set_key("start", frame == MATCH_START)
        else
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
    if transform_file and not i960_fifo_tap then install_transform_taps() end
    schedule_step()
end)
