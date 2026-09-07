-- Input bit mapper: resolve each named P1 field to its raw port bit.
--
-- Boots without playback, and once the ioport is up, sets each field in
-- turn and records which port bits change. Port state refreshes on the
-- frame poll, so every set/clear is separated from its read by settling
-- frames. Exits on its own after mapping.
--
-- Environment: VON_BITMAP_LOG (log file path)

local LOG_PATH = os.getenv("VON_BITMAP_LOG") or "vonj-bitmap.log"

local log_file = assert(io.open(LOG_PATH, "w"))

local function log(msg)
    log_file:write(msg .. "\n")
    log_file:flush()
end

local FIELD_ORDER = {
    "coin", "start",
    "down", "up", "right", "left",
    "left_shot", "left_dash",
    "right_shot", "right_dash",
    "r_down", "r_up", "r_right", "r_left",
}

local FIELD_PORT = {
    coin = ":IN0", start = ":IN0",
    down = ":IN1", up = ":IN1", right = ":IN1", left = ":IN1",
    left_shot = ":IN1", left_dash = ":IN1",
    right_shot = ":IN2", right_dash = ":IN2",
    r_down = ":IN2", r_up = ":IN2", r_right = ":IN2", r_left = ":IN2",
}

local FIELD_LABEL = {
    coin = "Coin 1", start = "1 Player Start",
    down = "P1 Left Stick/Down", up = "P1 Left Stick/Up",
    right = "P1 Left Stick/Right", left = "P1 Left Stick/Left",
    left_shot = "P1 Left Shot", left_dash = "P1 Left Dash",
    right_shot = "P1 Right Shot", right_dash = "P1 Right Dash",
    r_down = "P1 Right Stick/Down", r_up = "P1 Right Stick/Up",
    r_right = "P1 Right Stick/Right", r_left = "P1 Right Stick/Left",
}

local SETTLE = 5

local frame = 0
local step = 0
local current = nil
local current_field = nil
local before = nil

local function read_ports()
    local vals = {}
    local ok = pcall(function()
        vals[1] = manager.machine.ioport.ports[":IN0"]:read()
        vals[2] = manager.machine.ioport.ports[":IN1"]:read()
        vals[3] = manager.machine.ioport.ports[":IN2"]:read()
    end)
    if ok then
        return vals
    end
    return nil
end

emu.register_periodic(function()
    frame = frame + 1
    if frame < 300 then
        return
    end
    step = step + 1

    local idx = math.floor((step - 1) / (SETTLE * 3)) + 1
    local phase = (step - 1) % (SETTLE * 3)

    if idx > #FIELD_ORDER then
        log("bitmap: complete")
        manager.machine:exit()
        return
    end

    local key = FIELD_ORDER[idx]
    if key ~= current then
        current = key
        current_field = nil
        pcall(function()
            current_field = manager.machine.ioport.ports[FIELD_PORT[key]].fields[FIELD_LABEL[key]]
        end)
        if not current_field then
            log("bitmap: missing field " .. key)
            step = idx * SETTLE * 3
            return
        end
        before = read_ports()
        if before then
            log(string.format("bitmap: base in0 %x in1 %x in2 %x",
                before[1], before[2], before[3]))
        end
    end

    if not current_field then
        return
    end

    if phase == SETTLE then
        pcall(function() current_field:set_value(1) end)
    elseif phase == SETTLE * 2 then
        local during = read_ports()
        if before and during then
            local bits = {}
            for i = 1, 3 do
                local d = (before[i] ~ during[i]) & 0xffffffff
                if d ~= 0 then
                    bits[#bits + 1] = string.format("in%d mask %x", i - 1, d)
                end
            end
            log(string.format("bitmap: %-10s -> %s", key,
                #bits > 0 and table.concat(bits, " ") or "no change"))
        end
        pcall(function() current_field:set_value(0) end)
    end
end)
