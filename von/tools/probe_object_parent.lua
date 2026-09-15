-- Read the per-part "related record" pointer the geometry transform uses as a
-- parent (object+0x74; the code forms parent-relative world coords from it).
-- The object base -> OBA map comes from v-arcade-decomp emitter-g2-oba.json.
--
--   VON_OBJP_LOG=out.log mame vonj ... -autoboot_script
--     von/tools/probe_object_parent.lua

local LOG = assert(os.getenv("VON_OBJP_LOG"), "VON_OBJP_LOG required")
local SAMPLE_START = tonumber(os.getenv("VON_OBJP_START") or "2200")
local SAMPLE_END = tonumber(os.getenv("VON_OBJP_END") or "6000")
local COIN = tonumber(os.getenv("VON_PROGRESS_COIN_FRAME") or "900")
local START = tonumber(os.getenv("VON_PROGRESS_START_FRAME") or "1500")

-- base object pointer -> OBA (Temjin pool; from emitter-g2-oba.json).
local OBJECTS = {
    0x005046d0, 0x009e410d, 0x005046dc, 0x009e35b7, 0x005046e8, 0x009e2ea2,
    0x005046f4, 0x009e30ab, 0x00504700, 0x009e343a, 0x0050470c, 0x009e3588,
    0x00504718, 0x009e2a84, 0x00504724, 0x009e2f5d, 0x00504730, 0x009e3300,
    0x0050473c, 0x009e3054, 0x00504748, 0x009e332f, 0x00504754, 0x009e2cb1,
    0x00504930, 0x00a8ca04, 0x0050493c, 0x00a8c4ae, 0x00504948, 0x00a8c5fc,
    0x00504954, 0x00a8c519, 0x00504960, 0x00a8c353, 0x0050496c, 0x00a8c786,
    0x00504978, 0x00a8c848, 0x00504984, 0x00a8c7f1, 0x00504990, 0x00a8c62b,
    0x0050499c, 0x00a8bd4b,
}
local by_ptr = {}
for i = 1, #OBJECTS, 2 do by_ptr[OBJECTS[i]] = OBJECTS[i + 1] end

local FIELDS = {
    coin = { ":IN0", "Coin 1" },
    start = { ":IN0", "1 Player Start" },
}
local POSITIONS = { 0x74, 0x1b4, 0x0, 0x4, 0x8, 0xc, 0x10 }

local log_file = assert(io.open(LOG, "w"))
local function log(m) log_file:write(m .. "\n"); log_file:flush() end
log("objp: session start")

local frame = 0
local space
local fields = {}
local last = {}

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

local function rd(addr)
    local ok, v = pcall(function() return space:read_u32(addr) end)
    if ok then return v end
    return nil
end

local function sample()
    for i = 1, #OBJECTS, 2 do
        local base = OBJECTS[i]
        local oba = OBJECTS[i + 1]
        local vals = {}
        local changed = false
        for _, off in ipairs(POSITIONS) do
            local v = rd(base + off)
            vals[#vals + 1] = v
            if last[base .. ":" .. off] ~= v then changed = true end
            last[base .. ":" .. off] = v
        end
        if changed or frame == SAMPLE_START then
            local function fmt(v)
                if v == nil then return "--------" end
                local p = by_ptr[v]
                if p then return string.format("%08x", p) end
                return string.format("%08x", v)
            end
            log(string.format(
                "objp: frame=%d oba=%08x base=%08x 0x74=%s 0x1b4=%s 0=%08x 4=%08x 8=%08x c=%08x 10=%08x",
                frame, oba, base, fmt(vals[1]), fmt(vals[2]),
                vals[3] or 0, vals[4] or 0, vals[5] or 0, vals[6] or 0, vals[7] or 0))
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
    if frame == COIN then fields.coin:set_value(1) end
    if frame == COIN + 5 then fields.coin:clear_value() end
    if frame == START then fields.start:set_value(1) end
    if frame == START + 5 then fields.start:clear_value() end
    if frame >= SAMPLE_START and frame <= SAMPLE_END and (frame % 30 == 0) then
        sample()
    end
end)
