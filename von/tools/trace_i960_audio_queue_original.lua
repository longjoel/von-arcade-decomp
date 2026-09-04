-- Bounded diagnostic trace for the original vonj audio command producer.
--
-- This script is opt-in and read-only.  It samples the host byte-ring state
-- and records visited PCs in 0x2a4e0-0x2a574; it never runs against vonjdev
-- and does not alter emulated memory.

local cpu = assert(manager.machine.devices[":maincpu"])
local state = assert(cpu.state)
local space = assert(cpu.spaces[":program"] or cpu.spaces["program"])
local debug = cpu.debug
local seconds = tonumber(os.getenv("VON_AUDIO_QUEUE_SECONDS") or "5")
local max_samples = tonumber(os.getenv("VON_AUDIO_QUEUE_MAX_SAMPLES") or "4096")
local output_path = os.getenv("VON_AUDIO_QUEUE_LOG") or "vonj-audio-queue.log"
local frame = 0
local samples = 0
local written = false

local QUEUE_READ = 0x0051aa70
local QUEUE_WRITE = 0x0051aa74
local QUEUE_BASE = 0x0051aa80
local PC_BEGIN = 0x0002a4e0
local PC_END = 0x0002a574

local function current_pc()
    local entry = state["GENPC"] or state["CURPC"]
    return entry and tonumber(entry.value)
end

local function write_report()
    if written then return end
    written = true
    -- Samples are written incrementally by the periodic callback.  Append the
    -- final PC summary so stopping the machine cannot erase those records.
    local output = assert(io.open(output_path, "a"))
    output:write(string.format(
        "# source=original-vonj seconds=%.3f frames=%d samples=%d max_samples=%d\n",
        seconds, frame, samples, max_samples))
    if debug then
        for pc = PC_BEGIN, PC_END, 4 do
            if debug:track_pc_visited(pc) then
                output:write(string.format("pc_visited=%08x\n", pc))
            end
        end
    end
    output:close()
    if debug then debug:track_pc(false, false) end
end

if debug then debug:track_pc(true, true) end

emu.register_periodic(function()
    frame = frame + 1
    if samples < max_samples then
        local pc = current_pc()
        local read_index = space:read_u32(QUEUE_READ)
        local write_index = space:read_u32(QUEUE_WRITE)
        local slot = write_index % 64
        local byte = space:read_u8(QUEUE_BASE + slot)
        local output = io.open(output_path, "a")
        if samples == 0 then
            output = assert(output)
            output:write(string.format(
                "# source=original-vonj seconds=%.3f max_samples=%d\n",
                seconds, max_samples))
        else
            output = assert(output)
        end
        output:write(string.format(
            "sample=%d frame=%d time=%.6f pc=%s read=%08x write=%08x slot=%02x byte=%02x\n",
            samples, frame, emu.time(), pc and string.format("%08x", pc) or "unknown",
            read_index, write_index, slot, byte))
        output:close()
        samples = samples + 1
    end
    if emu.time() >= seconds or samples >= max_samples then
        manager.machine:exit()
    end
end)

_G.von_audio_queue_stop_subscription = emu.add_machine_stop_notifier(write_report)
