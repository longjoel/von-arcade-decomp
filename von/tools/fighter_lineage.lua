-- Per-part lineage tap for one selected fighter.
--
-- Drives the deterministic machine-select path (same timing as the decomp's
-- `action_schedule.lua`) so a non-default fighter is actually in the match, then
-- samples the i960 part records every frame.  For each record pointer it dumps
-- raw words, resolves OBA-bank values, and resolves pointers that fall back
-- into the sampled record set to a sibling index.  This is the live evidence
-- the offline clips cannot carry: which runtime record is a part's parent, and
-- which parts the emitter actually touches during gameplay.
--
-- Env:
--   VON_LINEAGE_LOG            (required) output log
--   VON_LINEAGE_SELECT_STEPS   right presses before confirm (default 0)
--   VON_LINEAGE_START_FRAME    confirm frame (default 2120)
--   VON_LINEAGE_SECONDS        emulated seconds (default 75)
--   VON_LINEAGE_PARTS          records per base (default 16)
--   VON_LINEAGE_STRIDE         record stride (default 0x0c)
--   VON_LINEAGE_BASE_PTRS      pointer cells to dereference (default player+enemy)
--   VON_LINEAGE_BASES          explicit record pointers (comma hex) — overrides
--   VON_LINEAGE_OFFSETS        record word offsets to dump (default below)
--   VON_LINEAGE_PARENT_OFFSET  word to read as the parent pointer (default 0x74)
--   VON_LINEAGE_SCAN           bytes scanned for OBA-bank values (default 0x20)
--   VON_LINEAGE_FAMILY         OBA family high word filter, e.g. 0x00a1
--   VON_LINEAGE_SAMPLE_STRIDE  frames between samples (default 1)

local LOG_PATH = assert(os.getenv("VON_LINEAGE_LOG"), "VON_LINEAGE_LOG required")
local SECONDS = tonumber(os.getenv("VON_LINEAGE_SECONDS") or "75")
local START_FRAME = tonumber(os.getenv("VON_LINEAGE_START_FRAME") or "1500")
local SELECT_STEPS = tonumber(os.getenv("VON_LINEAGE_SELECT_STEPS") or "0")
local SELECT_STEP_FRAMES = 45
local SELECT_LEAD = 420
local MATCH_FRAME = START_FRAME + SELECT_STEPS * SELECT_STEP_FRAMES
local PARTS = tonumber(os.getenv("VON_LINEAGE_PARTS") or "16")
local STRIDE = tonumber(os.getenv("VON_LINEAGE_STRIDE") or "0x0c")
local PARENT_OFFSET = tonumber(os.getenv("VON_LINEAGE_PARENT_OFFSET") or "0x74")
local SCAN = tonumber(os.getenv("VON_LINEAGE_SCAN") or "0x20")
local SAMPLE_STRIDE = tonumber(os.getenv("VON_LINEAGE_SAMPLE_STRIDE") or "1")
local FAMILY = tonumber(os.getenv("VON_LINEAGE_FAMILY") or "0")
local COIN_FRAME = tonumber(os.getenv("VON_PROGRESS_COIN_FRAME") or "900")

local function hexlist(name, fallback)
    local text = os.getenv(name)
    if not text or text == "" then return fallback end
    local out = {}
    for tok in string.gmatch(text, "([^,]+)") do out[#out + 1] = tonumber(tok) end
    return out
end

local OFFSETS = hexlist("VON_LINEAGE_OFFSETS", {
    0x00, 0x04, 0x08, 0x0c, 0x10, 0x18, 0x1c, 0x20, 0x74, 0x78, 0x1b4,
})
-- Player object stores its part-record base at +0x78 (mode 3 writes it at
-- 0x00503b48); the enemy equivalent is at 0x00504148.
local BASE_PTRS = hexlist("VON_LINEAGE_BASE_PTRS", { 0x00503b48, 0x00504148 })
local EXPLICIT_BASES = hexlist("VON_LINEAGE_BASES", {})

local log_file = assert(io.open(LOG_PATH, "w"))
local function log(msg) log_file:write(msg .. "\n"); log_file:flush() end
log(string.format("lineage: session start select_steps=%d family=%s",
    SELECT_STEPS, FAMILY > 0 and string.format("%04x", FAMILY) or "-"))

local fields = {}
local space
local frame = 0
local schedule_active = false
local current = "boot"

local FIELD_NAMES = {
    coin = { ":IN0", "Coin 1" }, start = { ":IN0", "1 Player Start" },
    right = { ":IN1", "P1 Left Stick/Right" },
}

local function setup()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then return false end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    if not space then return false end
    for key, spec in pairs(FIELD_NAMES) do
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

local function rd(addr)
    local ok, v = pcall(function() return space:read_u32(addr) end)
    if ok then return v end
    return nil
end

local function resolve_base(value, base_index)
    if not value or value == 0 then return "-" end
    if FAMILY > 0 and (value >> 16) == FAMILY then
        return string.format("oba:%08x", value)
    end
    local idx = base_index[value]
    if idx then return string.format("idx:%d", idx) end
    return string.format("%08x", value)
end

local explicit = #EXPLICIT_BASES > 0
local record_ptrs = {}

local function discover()
    record_ptrs = {}
    if explicit then
        for _, base in ipairs(EXPLICIT_BASES) do
            for k = 0, PARTS - 1 do record_ptrs[#record_ptrs + 1] = base + k * STRIDE end
        end
        return
    end
    for _, cell in ipairs(BASE_PTRS) do
        local base = rd(cell)
        if base and base >= 0x00500000 and base < 0x00600000 then
            for k = 0, PARTS - 1 do record_ptrs[#record_ptrs + 1] = base + k * STRIDE end
        end
    end
end

local function sample()
    local base_index = {}
    for i, ptr in ipairs(record_ptrs) do base_index[ptr] = i - 1 end
    local header_a = rd(0x0051ab08) or 0
    local header_b = rd(0x0051ab0c) or 0
    local cursor = rd(0x0051ab10) or 0
    local cells = {}
    for _, cell in ipairs(BASE_PTRS) do cells[#cells + 1] = string.format("%08x", rd(cell) or 0) end
    log(string.format("lineage: frame=%d action=%s headers=%08x,%08x cursor=%08x records=%d bases=%s",
        frame, current, header_a, header_b, cursor, #record_ptrs, table.concat(cells, ",")))
    for i, ptr in ipairs(record_ptrs) do
        local words = {}
        for _, off in ipairs(OFFSETS) do
            words[#words + 1] = string.format("%03x=%s", off, resolve_base(rd(ptr + off), base_index))
        end
        local obas = {}
        for off = 0, SCAN - 4, 4 do
            local v = rd(ptr + off)
            if v and FAMILY > 0 and (v >> 16) == FAMILY then
                obas[#obas + 1] = string.format("%03x:%08x", off, v)
            end
        end
        local parent = resolve_base(rd(ptr + PARENT_OFFSET), base_index)
        log(string.format("lineage: frame=%d idx=%d ptr=%08x parent=%s oba=%s %s",
            frame, i - 1, ptr, parent, table.concat(obas, ","), table.concat(words, " ")))
    end
end

local function boot_step()
    if frame < START_FRAME then
        set_key("coin", frame == COIN_FRAME)
        return false
    end
    local match_frame = MATCH_FRAME
    if SELECT_STEPS > 0 and frame < match_frame then
        local base = START_FRAME - SELECT_LEAD
        local right = false
        for step = 1, SELECT_STEPS do
            local at = base + step * SELECT_STEP_FRAMES
            if frame >= at and frame < at + 8 then right = true end
        end
        set_key("right", right)
    end
    -- Hold the confirm press for a few frames, exactly as gameplay_progress
    -- does; a single-frame pulse can be missed by the input sampler.
    set_key("start", frame >= match_frame and frame < match_frame + 5)
    if frame == match_frame + 5 then
        for key in pairs(FIELD_NAMES) do set_key(key, false) end
        current = "match"
        schedule_active = true
        log(string.format("lineage: frame=%d action=match begin", frame))
    end
    return frame >= match_frame + 5
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        if frame % 60 == 1 then setup() end
        return
    end
    if not fields.coin then return end
    if not boot_step() then return end
    local first = MATCH_FRAME + 5
    if frame == first or (frame > first and (frame - first) % SAMPLE_STRIDE == 0) then
        discover()
        if #record_ptrs > 0 then sample() end
    end
end)
