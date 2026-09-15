-- Watch the candidate "lock on" signals through a jump: the aim-tracking gate
-- (object+0xa0/+0xa1), the related/target pointer (object+0x74), and the
-- camera yaw (eye 0x504b98/b0, target 0x504bb4/bc), plus the opponent bearing.
--
--   VON_LOCK_LOG=out.log mame vonj ... -autoboot_script \
--     von/tools/probe_jump_lock.lua

local LOG = assert(os.getenv("VON_LOCK_LOG"), "VON_LOCK_LOG required")
local COIN = tonumber(os.getenv("VON_LOCK_COIN") or "7200")
local START = tonumber(os.getenv("VON_LOCK_START") or "7400")
local JUMP = tonumber(os.getenv("VON_LOCK_JUMP") or "9600")
local PLAYER = 0x00503ad0
local OPP = 0x005040d0

local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "2 Players Start" },
    l_left = { ":IN1", "P1 Left Stick/Left" },
    r_right = { ":IN2", "P1 Right Stick/Right" },
}

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("lock: session start")

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
    set_key("l_left", chord)
    set_key("r_right", chord)

    if frame >= JUMP - 5 and frame <= JUMP + 135 then
        log(string.format(
            "lock: f%d y=0x%08x px=0x%08x pz=0x%08x ox=0x%08x oz=0x%08x tgt=0x%08x a0=%d a1=%d cex=0x%08x cez=0x%08x ctx=0x%08x ctz=0x%08x",
            frame,
            space:read_u32(PLAYER + 0x0c), space:read_u32(PLAYER + 0x08), space:read_u32(PLAYER + 0x10),
            space:read_u32(OPP + 0x08), space:read_u32(OPP + 0x10),
            space:read_u32(PLAYER + 0x74),
            space:read_u8(PLAYER + 0xa0), space:read_u8(PLAYER + 0xa1),
            space:read_u32(0x00504b98), space:read_u32(0x00504ba0),
            space:read_u32(0x00504bb4), space:read_u32(0x00504bbc)))
    end
end)
