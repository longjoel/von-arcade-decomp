-- Read the ordnance pool (mech object + 0x200, 32 records x 0x20) while each
-- weapon fires, to map the projectile type byte (damage-table index) to the
-- weapon.  Player mech = 0x503ad0, opponent = 0x5040d0 (recovered-camera.md);
-- the hit applier reads record byte 0 and indexes the table at 0x565ed0.
--
--   VON_PTYPE_LOG=out.log mame vonj ... -autoboot_script \
--     von/tools/probe_projectile_type.lua

local LOG = assert(os.getenv("VON_PTYPE_LOG"), "VON_PTYPE_LOG required")
local SECONDS = tonumber(os.getenv("VON_PTYPE_SECONDS") or "190")
local COIN = tonumber(os.getenv("VON_PROGRESS_COIN_FRAME") or "7200")
local START = tonumber(os.getenv("VON_PROGRESS_START_FRAME") or "7400")

-- Phase boundaries (battle starts ~9500).  Hold one weapon per window.
local PHASES = {
    { 9600, 9900, "left" },
    { 9900, 10200, "right" },
    { 10200, 10500, "both" },
    { 10500, 10800, "none" },
}

local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "2 Players Start" },
    left_shot = { ":IN1", "P1 Left Shot" },
    right_shot = { ":IN2", "P1 Right Shot" },
}
local POOLS = { { "player", 0x00503ad0 }, { "enemy", 0x005040d0 } }

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("ptype: session start")

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

local function phase_for(f)
    for _, p in ipairs(PHASES) do
        if f >= p[1] and f < p[2] then return p[2], p[3] end
    end
    return nil, nil
end

local function scan(tag)
    for _, pool in ipairs(POOLS) do
        local name, base = pool[1], pool[2]
        local parts = {}
        for i = 0, 31 do
            -- r6 array (base+0x200, byte) and r5 array (base+0x202, word); the
            -- hit applier indexes the damage table by the low byte of +0x202.
            local ok, flag = pcall(function() return space:read_u8(base + 0x200 + i * 0x20) end)
            local ok2, ty = pcall(function() return space:read_u16(base + 0x202 + i * 0x20) end)
            if ok and ok2 and (flag ~= 0 or ty ~= 0) then
                parts[#parts + 1] = string.format("%d:%02x/%04x", i, flag or 0, ty or 0)
            end
        end
        if #parts > 0 then
            log(string.format("ptype: f%d %s %s types=%s",
                frame, tag, name, table.concat(parts, ",")))
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

    local _, weapon = phase_for(frame)
    if weapon then
        set_key("left_shot", weapon == "left" or weapon == "both")
        set_key("right_shot", weapon == "right" or weapon == "both")
        -- tap every 24 frames so the edge registers without holding cadence
        if (frame % 24) >= 3 then
            set_key("left_shot", false)
            set_key("right_shot", false)
        end
        if frame % 12 == 0 then scan(weapon) end
    end
end)
