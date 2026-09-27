-- Measure applied damage vs. player->opponent range.
--
-- Parks the player at a ladder of ranges in front of a stationary opponent,
-- fires the right weapon (and optionally left), and logs the opponent's
-- working-health cell so each landed hit's drop can be paired with the range at
-- impact. If damage falls off with distance, the drops will not be constant.
--
--   VON_DMGR_LOG=out.log mame vonj ... -autoboot_script \
--     von/tools/probe_weapon_damage_range.lua

local LOG = assert(os.getenv("VON_DMGR_LOG"), "VON_DMGR_LOG required")
local COIN = tonumber(os.getenv("VON_DMGR_COIN") or "7200")
local START = tonumber(os.getenv("VON_DMGR_START") or "7400")
local BATTLE = tonumber(os.getenv("VON_DMGR_BATTLE") or "9500")
local WEAPON = os.getenv("VON_DMGR_WEAPON") or "right"
local SETTLE = tonumber(os.getenv("VON_DMGR_SETTLE") or "12")
local RESOLVE = tonumber(os.getenv("VON_DMGR_RESOLVE") or "150")
local RANGES = {}
for tok in string.gmatch(os.getenv("VON_DMGR_RANGES")
        or "15,25,40,65,95,130,170,210,250,290", "([^,]+)") do
    RANGES[#RANGES + 1] = tonumber(tok)
end

local PLAYER_X = 0x00503ad8
local PLAYER_Y = 0x00503adc
local PLAYER_Z = 0x00503ae0
local PLAYER_HEAD = 0x00503c28
local OPP_X = 0x005040d8
local OPP_Z = 0x005040e0
local PL_WORK = 0x00503ca0
local OPP_WORK = 0x005042a0

local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "2 Players Start" },
    left_shot = { ":IN1", "P1 Left Shot" },
    right_shot = { ":IN2", "P1 Right Shot" },
}

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("dmgr: session start weapon=" .. WEAPON)

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

local function read_f32(addr)
    return (string.unpack("<f", string.pack("<I", space:read_u32(addr))))
end

local function write_f32(addr, value)
    pcall(function() space:write_u32(addr, string.unpack("<I", string.pack("<f", value))) end)
end

-- Place the player `range` units in front of the opponent on -Z, facing +Z
-- (the same orientation as the working spawn pose: player at -Z, opponent +Z).
local function place(range)
    local ex = read_f32(OPP_X)
    local ez = read_f32(OPP_Z)
    local px = ex
    local pz = ez - range
    write_f32(PLAYER_X, px)
    write_f32(PLAYER_Y, 0.0)
    write_f32(PLAYER_Z, pz)
    write_f32(PLAYER_HEAD, math.deg(math.atan(ex - px, ez - pz)))
end

-- Ladder: each entry is a window; steps 0..SETTLE hold position, then fire,
-- then resolve while logging.
local ladder_start = BATTLE
local per_range = SETTLE + RESOLVE

local function phase_for(f)
    local offset = f - ladder_start
    if offset < 0 then return nil end
    local index = math.floor(offset / per_range)
    if index >= #RANGES then return nil end
    local local_frame = offset - index * per_range
    return index, local_frame
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
    if frame < ladder_start then return end

    local index, local_frame = phase_for(frame)
    if not index then
        set_key("left_shot", false)
        set_key("right_shot", false)
        return
    end
    local range = RANGES[index + 1]
    if local_frame < SETTLE then
        -- Reposition, face, and keep the target topped up so no round ends.
        place(range)
        pcall(function() space:write_u16(OPP_WORK, 1000) end)
        set_key("left_shot", false)
        set_key("right_shot", false)
    else
        local firing = (local_frame - SETTLE) < 3
        set_key("left_shot", firing and WEAPON == "left")
        set_key("right_shot", firing and WEAPON == "right")
    end

    if frame % 2 == 0 then
        local px = read_f32(PLAYER_X)
        local pz = read_f32(PLAYER_Z)
        local ex = read_f32(OPP_X)
        local ez = read_f32(OPP_Z)
        local dist = math.sqrt((px - ex) * (px - ex) + (pz - ez) * (pz - ez))
        local ord = 0
        for i = 0, 31 do
            if space:read_u8(0x503ad0 + 0x200 + i * 0x20) ~= 0 then ord = ord + 1 end
        end
        log(string.format("dmgr: f%d idx=%d range=%g dist=%.1f ow=%d pw=%d ord=%d head=%.0f",
            frame, index, range, dist, space:read_u16(OPP_WORK),
            space:read_u16(PL_WORK), ord, read_f32(PLAYER_HEAD)))
    end
end)
