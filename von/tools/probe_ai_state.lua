-- Per-frame opponent-AI state probe.
--
-- Logs the CPU object's decision inputs and outputs plus the AI globals, so
-- the sector -> class -> command chain can be checked against the decoded
-- tables in von/i960/opponent-ai.md.
--
--   VON_AI_LOG=out.log VON_AI_SECONDS=40 ./bin/vonctl run -video none \
--     -sound none -skip_gameinfo -seconds_to_run 40 \
--     -autoboot_script von/tools/probe_ai_state.lua

local SECONDS = tonumber(os.getenv("VON_AI_SECONDS") or "40")
local LOG_PATH = os.getenv("VON_AI_LOG") or "von-ai-state.log"

local PLAYER = 0x00503ad0
local CPU = 0x005040d0
-- AI globals (von/i960/opponent-ai.md).
local G_SECTOR = 0x00504d68   -- 0x73508 classification (0..9)
local G_CLASS = 0x00504d94    -- current behaviour class (0..33)
local G_DIST = 0x00504d60     -- SHARC response / threshold
local G_MODE = 0x00504e30
local G_GLOBAL = 0x00504d9c
local G_TRANS = 0x00504d98    -- state-machine transition output
local G_COUNTER = 0x00504db4  -- action counter
local G_MA = 0x00504dac       -- movement bytes
local G_MB = 0x00504db0

local file = assert(io.open(LOG_PATH, "w"))
local frame = 0
local space

local function setup()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then
        return false
    end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    return space ~= nil
end

local function r16(address)
    local ok, value = pcall(function() return space:read_u16(address) end)
    return ok and value or 0xffff
end

local function r32(address)
    local ok, value = pcall(function() return space:read_u32(address) end)
    return ok and value or 0xffffffff
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        if frame % 60 == 1 then
            setup()
        end
        return
    end
    file:write(string.format(
        "frame=%d sector=%d class=%d trans=%d counter=%d ma=%02x mb=%02x " ..
        "dist=%08x mode=%08x gstate=%08x " ..
        "A64=%d A172=%d A170=%d A17a=%d A108=%04x A184=%04x Ax=%08x Az=%08x " ..
        "B64=%d B172=%d B170=%d B17a=%d B108=%04x B184=%04x Bx=%08x Bz=%08x\n",
        frame,
        r16(G_SECTOR), r16(G_CLASS), r16(G_TRANS), r16(G_COUNTER),
        r16(G_MA) & 0xff, r16(G_MB) & 0xff,
        r32(G_DIST), r32(G_MODE), r32(G_GLOBAL),
        r16(PLAYER + 0x64), r16(PLAYER + 0x172), r16(PLAYER + 0x170),
        r16(PLAYER + 0x17a), r16(PLAYER + 0x108), r16(PLAYER + 0x184),
        r32(PLAYER + 0x08), r32(PLAYER + 0x10),
        r16(CPU + 0x64), r16(CPU + 0x172), r16(CPU + 0x170),
        r16(CPU + 0x17a), r16(CPU + 0x108), r16(CPU + 0x184),
        r32(CPU + 0x08), r32(CPU + 0x10)))
    if frame % 60 == 0 then
        file:flush()
    end
    if frame >= SECONDS * 60 then
        file:flush()
        manager.machine:exit()
    end
end)
