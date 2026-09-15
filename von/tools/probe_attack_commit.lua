-- Input-commit audit: does the mech accept movement while an attack runs?
--
-- Confirms the fire first (player ordnance slot byte 0 and the left cooldown
-- timer 0x503cba = object+0x1ea), then logs position through the attack.
-- Phases:
--   A stand still + fire left      -> confirms the shot without any stick
--   B hold forward + fire left     -> movement during the attack
--   C hold forward alone (control)  -> movement baseline
--
-- Player x/z = object+0x08/+0x10, action = object+0x174.
--
--   VON_AC_LOG=out.log mame vonj ... -autoboot_script \
--     von/tools/probe_attack_commit.lua

local LOG = assert(os.getenv("VON_AC_LOG"), "VON_AC_LOG required")
local COIN = tonumber(os.getenv("VON_AC_COIN") or "7200")
local START = tonumber(os.getenv("VON_AC_START") or "7400")
local PLAYER = 0x00503ad0

local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "2 Players Start" },
    l_up = { ":IN1", "P1 Left Stick/Up" },
    r_up = { ":IN2", "P1 Right Stick/Up" },
    l_shot = { ":IN1", "P1 Left Shot" },
}

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("ac: session start")

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

local function shots()
    local n = 0
    for i = 0, 31 do
        if space:read_u8(PLAYER + 0x200 + i * 0x20) ~= 0 then n = n + 1 end
    end
    return n
end

-- Walk forward from 9600 (launch + settle), then fire at 9750 to isolate how an
-- attack changes the horizontal speed.
local function inputs(f)
    local fwd = f >= 9600 and f < 10000
    local fire = f >= 9750 and f < 9754
    return fwd, fire
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

    local fwd, fire = inputs(frame)
    set_key("l_up", fwd)
    set_key("r_up", fwd)
    set_key("l_shot", fire)

    if frame >= 9600 and frame <= 10020 then
        log(string.format("ac: f%d x=0x%08x z=0x%08x act=%d cd=0x%04x shots=%d",
            frame, space:read_u32(PLAYER + 0x08), space:read_u32(PLAYER + 0x10),
            space:read_u8(PLAYER + 0x174), space:read_u16(PLAYER + 0x1ea), shots()))
    end
end)
