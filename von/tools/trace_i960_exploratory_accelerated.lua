-- Exploratory-only accelerated attract sampler.
--
-- This deliberately writes the documented work-RAM heartbeat state so later
-- attract arms can be exercised against an original-ROM staging run. Its
-- PCS/events are exploratory evidence, never authoritative strict evidence.

local cpu = assert(manager.machine.devices[":maincpu"])
local state = assert(cpu.state)
local space = assert(cpu.spaces[":program"] or cpu.spaces["program"])
local seconds = tonumber(os.getenv("VON_EXPLORATORY_SECONDS") or "60")
local pcs_path = os.getenv("VON_EXPLORATORY_PC_LOG") or
    "exploratory-accelerated-pcs.txt"
local events_path = os.getenv("VON_EXPLORATORY_EVENTS_LOG") or
    "exploratory-accelerated-events.log"
local pcs = assert(io.open(pcs_path, "w"))
local events = assert(io.open(events_path, "w"))

local INIT = 0x00500090
local HEARTBEAT = 0x00500094
local PHASE = 0x005000a4
local thresholds = { 0x00057e3f, 0x000be6df, 0x00155cbf, 0x00249eff }
local phase = -1
local next_phase = 0
local frame = 0

local function current_pc()
    local entry = state["GENPC"] or state["CURPC"]
    return entry and entry.value
end

local function event(message)
    events:write(string.format("time=%.6f frame=%d %s\n", emu.time(), frame, message))
    events:flush()
end

emu.register_periodic(function()
    frame = frame + 1
    local pc = current_pc()
    if pc then
        pcs:write(string.format("%08x\n", tonumber(pc)))
        pcs:flush()
    end

    local init = space:read_u32(INIT)
    local observed = space:read_u32(PHASE)
    if init == 0x494e4954 and next_phase < #thresholds and observed == phase then
        local target = thresholds[next_phase + 1]
        space:write_u32(HEARTBEAT, target + 1)
        event(string.format("heartbeat_injection phase=%d threshold=0x%08x value=0x%08x",
            next_phase + 1, target, target + 1))
        phase = phase + 1
        next_phase = next_phase + 1
    elseif observed > phase then
        phase = observed
    end

    if emu.time() >= seconds then
        event("complete exploratory=true")
        pcs:close()
        events:close()
        manager.machine:exit()
    end
end)
