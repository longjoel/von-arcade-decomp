-- Test whether a fresh weapon tap ever spawns while airborne, and at what
-- height: the "apex window" hypothesis.
--
-- Jump (outward flick) then tap the left shot every few frames through the
-- airborne phase; scan the player's ordnance pool for any spawned projectile.
-- A spawn at a particular y would be an air-attack window; none would mean the
-- jump is fully committed.
--
--   VON_AIR_LOG=out.log mame vonj ... -autoboot_script \
--     von/tools/probe_air_attack.lua

local LOG = assert(os.getenv("VON_AIR_LOG"), "VON_AIR_LOG required")
local COIN = tonumber(os.getenv("VON_AIR_COIN") or "7200")
local START = tonumber(os.getenv("VON_AIR_START") or "7400")
local PLAYER = 0x00503ad0
local JUMP = tonumber(os.getenv("VON_AIR_JUMP") or "9600")

local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "2 Players Start" },
    l_left = { ":IN1", "P1 Left Stick/Left" },
    r_right = { ":IN2", "P1 Right Stick/Right" },
    l_shot = { ":IN1", "P1 Left Shot" },
}

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("air: session start")

local frame = 0
local space
local fields = {}

local function setup()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then return false end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    for key, spec in pairs(FIELDS) do
        local port = manager.machine.ioport.ports[spec[1]]
        fields[key] = port and port.fields[spec[2]] or nil
    end
    return space ~= nil and fields.coin ~= nil
end

local function set_key(key, on)
    local f = fields[key]
    if not f then return end
    if on then f:set_value(1) else f:clear_value() end
end

local function scan()
    for i = 0, 31 do
        local b0 = space:read_u8(PLAYER + 0x200 + i * 0x20)
        if b0 ~= 0 then
            local y = space:read_u32(PLAYER + 0x0c)
            log(string.format("air: f%d spawn slot=%d b0=%d y=0x%08x", frame, i, b0, y))
        end
    end
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        if frame % 60 == 1 then setup() end
        return
    end
    if not fields.coin then return end
    if frame == COIN then set_key("coin", true) end
    if frame == COIN + 8 then set_key("coin", false) end
    if frame == START then set_key("start", true) end
    if frame == START + 8 then set_key("start", false) end

    local chord = frame >= JUMP and frame < JUMP + 10
    set_key("l_left", chord)
    set_key("r_right", chord)
    -- Tap the left shot every 6 frames through takeoff + flight.
    local tap = frame >= JUMP + 12 and frame < JUMP + 130 and (frame % 6) < 2
    set_key("l_shot", tap)

    if frame % 600 == 0 then log("air: heartbeat f" .. frame) end
    if frame >= JUMP - 5 and frame <= JUMP + 140 then
        local y = space:read_u32(PLAYER + 0x0c)
        log(string.format("air: f%d y=0x%08x tap=%d", frame, y, tap and 1 or 0))
        scan()
    end
end)
