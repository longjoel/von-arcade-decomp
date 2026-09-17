-- Per-frame hand-move record probe.
--
-- Logs the 0x504e50 aggregate flags and every nonzero record in both objects'
-- 32-entry hand-move table (object+0x200, 0x20 stride: flags byte, id at +2),
-- so the flag vocabulary and the event-handler writes can be checked against
-- von/i960/opponent-ai.md.
--
--   VON_HAND_LOG=out.log VON_HAND_SECONDS=40 ./bin/vonctl run -video none \
--     -sound none -skip_gameinfo -seconds_to_run 40 \
--     -autoboot_script von/tools/probe_hand_moves.lua

local SECONDS = tonumber(os.getenv("VON_HAND_SECONDS") or "40")
local LOG_PATH = os.getenv("VON_HAND_LOG") or "von-hand-moves.log"

local PLAYER = 0x00503ad0
local CPU = 0x005040d0
local AGGREGATE = 0x00504e50

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

local function u8(address)
    local ok, value = pcall(function() return space:read_u8(address) end)
    return ok and value or 0xff
end

local function u16(address)
    local ok, value = pcall(function() return space:read_u16(address) end)
    return ok and value or 0xffff
end

local function records(base)
    local parts = {}
    for i = 0, 31 do
        local address = base + 0x200 + i * 0x20
        local flags = u8(address)
        if flags ~= 0 then
            parts[#parts + 1] = string.format("%d:%02x/%04x", i, flags,
                u16(address + 2))
        end
    end
    return table.concat(parts, ",")
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        if frame % 60 == 1 then
            setup()
        end
        return
    end
    local a = records(PLAYER)
    local b = records(CPU)
    if a ~= "" or b ~= "" or u8(AGGREGATE) ~= 0 then
        file:write(string.format("frame=%d agg=%02x A[%s] B[%s]\n",
            frame, u8(AGGREGATE), a, b))
        file:flush()
    end
    if frame >= SECONDS * 60 then
        file:flush()
        manager.machine:exit()
    end
end)
