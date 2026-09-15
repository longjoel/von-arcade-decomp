-- Does the jump accept horizontal movement in the air, and is there a landing
-- lock? Jump (outward flick), then hold forward and log y/z through the arc and
-- landing.
--
-- Player y = object+0x0c, z = object+0x10.
--
--   VON_LAND_LOG=out.log mame vonj ... -autoboot_script \
--     von/tools/probe_landing.lua

local LOG = assert(os.getenv("VON_LAND_LOG"), "VON_LAND_LOG required")
local COIN = tonumber(os.getenv("VON_LAND_COIN") or "7200")
local START = tonumber(os.getenv("VON_LAND_START") or "7400")
local PLAYER = 0x00503ad0
local JUMP = tonumber(os.getenv("VON_LAND_JUMP") or "9600")

local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "2 Players Start" },
    l_left = { ":IN1", "P1 Left Stick/Left" },
    r_right = { ":IN2", "P1 Right Stick/Right" },
    l_up = { ":IN1", "P1 Left Stick/Up" },
    r_up = { ":IN2", "P1 Right Stick/Up" },
}

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("land: session start")

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
    local fwd = frame >= JUMP + 12 and frame < JUMP + 150
    set_key("l_left", chord)
    set_key("r_right", chord)
    set_key("l_up", fwd)
    set_key("r_up", fwd)

    if frame >= JUMP - 5 and frame <= JUMP + 150 then
        log(string.format("land: f%d y=0x%08x z=0x%08x act=%d",
            frame, space:read_u32(PLAYER + 0x0c), space:read_u32(PLAYER + 0x10),
            space:read_u8(PLAYER + 0x174)))
    end
end)
