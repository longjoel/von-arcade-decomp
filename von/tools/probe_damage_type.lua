-- Map projectile type -> weapon by tapping the damage-table read.
--
-- The hit applier (i960 0xbe0f4 / 0xbe174) reads `table[type*16]` from the
-- runtime table at 0x565ed0, so the tapped read *offset* gives the type
-- directly, and the i960 registers at that instant hold the projectile (g1),
-- defender (g2) and attacker/owner (g0).  Works headless (no debugger).
--
--   VON_DTYPE_LOG=out.log mame vonj ... -autoboot_script \
--     von/tools/probe_damage_type.lua

local LOG = assert(os.getenv("VON_DTYPE_LOG"), "VON_DTYPE_LOG required")
local COIN = tonumber(os.getenv("VON_PROGRESS_COIN_FRAME") or "7200")
local START = tonumber(os.getenv("VON_PROGRESS_START_FRAME") or "7400")
local FIRE0 = tonumber(os.getenv("VON_DTYPE_FIRE") or "9600")
local FIRE_N = tonumber(os.getenv("VON_DTYPE_FRAMES") or "900")

local TABLE_BASE = 0x00565ed0
local TABLE_LEN = 0x334 * 4

local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "2 Players Start" },
    left_shot = { ":IN1", "P1 Left Shot" },
    right_shot = { ":IN2", "P1 Right Shot" },
}
local P1, P2 = 0x00503ad0, 0x005040d0

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("dtype: session start")

local frame = 0
local space
local cpu
local fields = {}
local tap
local reading = false
local hits = 0

local function setup()
    cpu = manager.machine.devices[":maincpu"]
    if not cpu then return false end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    for key, spec in pairs(FIELDS) do
        local port = manager.machine.ioport.ports[spec[1]]
        fields[key] = port and port.fields[spec[2]] or nil
    end
    if not space then return false end
    tap = space:install_read_tap(TABLE_BASE, TABLE_BASE + TABLE_LEN - 1, "dmgtype",
        function(address, data, mask)
            if reading then return end
            reading = true
            local function st(name)
                local e = cpu.state[name]
                return e and tonumber(e.value) or -1
            end
            local off = address >= TABLE_BASE and (address - TABLE_BASE) or address
            local ty = math.floor(off / 16)
            hits = hits + 1
            log(string.format(
                "dtype: f%d type=%d(0x%02x) addr=%08x val=%08x g1=%08x g2=%08x g0=%08x pc=%08x",
                frame, ty, ty, address, data, st("g1"), st("g2"), st("g0"), st("CURPC")))
            reading = false
            return data
        end)
    return tap ~= nil
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

    if frame >= FIRE0 and frame < FIRE0 + FIRE_N then
        local on = (frame % 24) < 3
        set_key("left_shot", on)
        set_key("right_shot", on)
    end
end)
