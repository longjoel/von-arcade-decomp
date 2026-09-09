-- Service-menu navigator for link setup.
--
-- Env: VON_SVC_LOG   log path
--      VON_SVC_SNAP  snapshot directory (png per step + periodic)
--      VON_SVC_STEPS comma list KEY:FRAMES, e.g. "test:8,down:8,shot:8".
--        Keys: test, service, coin, start, up, down, left, right,
--        left_shot, right_shot, left_dash, right_dash,
--        r_up, r_down, r_left, r_right
--      VON_SVC_SECONDS total seconds (default 60)
--
-- First run with STEPS unset to dump all IN0 field names.

local LOG_PATH = os.getenv("VON_SVC_LOG") or "vonj-svc.log"
local SNAP_DIR = os.getenv("VON_SVC_SNAP") or "vonj-svc-snaps"
local STEPS_RAW = os.getenv("VON_SVC_STEPS") or ""
local SECONDS = tonumber(os.getenv("VON_SVC_SECONDS") or "60")
local START_AT = tonumber(os.getenv("VON_SVC_START") or "1")
local SAVE_AT = tonumber(os.getenv("VON_SVC_SAVE_AT") or "0")
local SAVE_NAME = os.getenv("VON_SVC_SAVE_NAME") or "svc"
local LOAD_AT = tonumber(os.getenv("VON_SVC_LOAD_AT") or "0")

local NAMES = {
    test       = { ":IN0", "Service Mode" },
    service    = { ":IN0", "Service 1" },
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
    r_down     = { ":IN2", "P1 Right Stick/Down" },
    r_up       = { ":IN2", "P1 Right Stick/Up" },
    r_right    = { ":IN2", "P1 Right Stick/Right" },
    r_left     = { ":IN2", "P1 Right Stick/Left" },
}

local log_file = assert(io.open(LOG_PATH, "w"))
local function log(msg)
    log_file:write(msg .. "\n")
    log_file:flush()
end

local TILE_BASE = 0x01000000
local ROWS, COLS = 64, 64

local space = nil

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

local steps = {}
for tok in string.gmatch(STEPS_RAW, "([^,]+)") do
    local key, n = string.match(tok, "^([^:]+):(%d+)$")
    if key and n then steps[#steps + 1] = { key = key, frames = tonumber(n) } end
end

local frame = 0
local fields = {}
local step_idx = 0
local step_left = 0
local current = nil

local function snap(tag)
    pcall(function() manager.machine.video:snapshot() end)
    log(string.format("svc: frame %d snap %s", frame, tag))
end

emu.register_periodic(function()
    frame = frame + 1
    if frame == 1 then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
        end
        for _, pname in ipairs({ ":IN0", ":IN1", ":IN2" }) do
            local ok, port = pcall(function()
                return manager.machine.ioport.ports[pname]
            end)
            if ok and port then
                for name, _ in pairs(port.fields) do
                    log("svc: field " .. pname .. " [" .. name .. "]")
                end
            end
        end
        log("svc: test button is [Service Mode]")
        for key, spec in pairs(NAMES) do
            local ok, port = pcall(function()
                return manager.machine.ioport.ports[spec[1]]
            end)
            if ok and port and spec[2] then
                local okf, field = pcall(function()
                    return port.fields[spec[2]]
                end)
                if okf and field then fields[key] = field end
            end
        end
        snap("boot")
    end

    if current and step_left > 0 then
        step_left = step_left - 1
        if step_left == 0 and fields[current] then
            fields[current]:clear_value()
            log(string.format("svc: frame %d release %s", frame, current))
            snap("after-" .. current)
            current = nil
        end
    elseif step_idx < #steps and frame >= START_AT then
        step_idx = step_idx + 1
        current = steps[step_idx].key
        step_left = steps[step_idx].frames
        if current == "wait" then
            log(string.format("svc: frame %d wait %d f", frame, step_left))
        elseif fields[current] then
            fields[current]:set_value(1)
            log(string.format("svc: frame %d press %s (%d f)",
                frame, current, step_left))
        else
            log(string.format("svc: frame %d MISSING field %s", frame, current))
            current = nil
            step_left = 0
        end
    end

    if LOAD_AT > 0 and frame == LOAD_AT then
        pcall(function() manager.machine:load(SAVE_NAME) end)
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
        end
        log(string.format("svc: frame %d loaded %s", frame, SAVE_NAME))
    end
    if SAVE_AT > 0 and frame == SAVE_AT then
        pcall(function() manager.machine:save(SAVE_NAME) end)
        log(string.format("svc: frame %d saved %s", frame, SAVE_NAME))
    end
    if frame % 30 == 0 then
        if space == nil then
            log(string.format("svc: frame %d space is NIL", frame))
        else
            local okv, v0 = pcall(function()
                return space:read_u16(TILE_BASE)
            end)
            log(string.format("svc: frame %d tile0 read ok=%s v=%s",
                frame, tostring(okv),
                okv and string.format("%04x", v0) or "-"))
        end
        local ok, text = pcall(screen_text)
        if ok then
            local shown = {}
            for line in string.gmatch(text, "[^\n]+") do
                if line:match("%S") then shown[#shown + 1] = line end
            end
            if #shown > 0 then
                log(string.format("svc: frame %d tiles >>>\n%s\n<<< END",
                    frame, table.concat(shown, "\n")))
            end
        end
    end
    if frame % 150 == 0 then snap("periodic-" .. frame) end
    if frame >= SECONDS * 60 then
        log("svc: session complete")
        manager.machine:exit()
    end
end)
