-- Deterministic original-ROM single-player evidence capture.
--
-- The first screen lasts roughly ten seconds on the original ROM. Let it
-- finish on its known timing, then begin tracing and insert the coin so the
-- resulting state change can be observed even if the tilemap stays static.

local ROOT = assert(os.getenv("VON_CAPTURE_DIR"), "VON_CAPTURE_DIR is required")
local SELECT_STEPS = tonumber(os.getenv("VON_CAPTURE_SELECT_STEPS") or "0")
local START_TRACE_FRAME = tonumber(os.getenv("VON_CAPTURE_START_TRACE_FRAME") or "600")
local TITLE_DWELL_FRAMES = tonumber(os.getenv("VON_CAPTURE_TITLE_DWELL_FRAMES") or "600")
local MAX_POST_START_FRAMES = tonumber(os.getenv("VON_CAPTURE_POST_START_FRAMES") or "1800")

local TILE_BASE = 0x01000000
local TILE_BYTES = 0x2000
local WORKRAM_BASE = 0x00500000
local WORKRAM_BYTES = 0x00100000
local GEO_BUFFER_BASE = 0x00509ba0
local GEO_BUFFER_BYTES = 0x8000
local TEXTURE0_BASE = 0x11000000
local TEXTURE1_BASE = 0x11200000
local TEXTURE_BYTES = 0x20000

local frame = 0
local cpu = manager.machine.devices[":maincpu"]
local state = assert(cpu and cpu.state, "i960 CPU state unavailable")
local space = assert(cpu and (cpu.spaces[":program"] or cpu.spaces["program"]),
    "i960 program space unavailable")
local debug = cpu.debug
local events = assert(io.open(ROOT .. "/events.log", "w"))
local phase = "warmup"
local phase_start = 0
local coin_frame
local start_frame
local next_selection_step = 1
local pressed_until = {}
local fields = {}
local queue_trace = os.getenv("VON_CAPTURE_QUEUE_TRACE") == "1"
local queue_log
local queue_samples = 0
local queue_max_samples = tonumber(os.getenv("VON_CAPTURE_QUEUE_MAX_SAMPLES") or "4096")
local queue_sample_interval = tonumber(os.getenv("VON_CAPTURE_QUEUE_SAMPLE_INTERVAL") or "4")
local QUEUE_READ = 0x0051aa70
local QUEUE_WRITE = 0x0051aa74
local QUEUE_BASE = 0x0051aa80
local QUEUE_PC_BEGIN = 0x0002a4e0
local QUEUE_PC_END = 0x0002a574

if queue_trace then
    assert(queue_max_samples > 0, "VON_CAPTURE_QUEUE_MAX_SAMPLES must be positive")
    queue_log = assert(io.open(os.getenv("VON_CAPTURE_QUEUE_LOG") or
        (ROOT .. "/audio-queue.log"), "w"))
    queue_log:write(string.format(
        "# source=original-vonj selector_steps=%d max_samples=%d\n",
        SELECT_STEPS, queue_max_samples))
end

local function log(kind, detail)
    events:write(string.format("frame=%d phase=%s event=%s %s\n", frame, phase, kind, detail or ""))
    events:flush()
end

local function fnv_tilemap()
    local hash = 2166136261
    for offset = 0, TILE_BYTES - 2, 2 do
        hash = (hash ~ space:read_u16(TILE_BASE + offset)) * 16777619 % 4294967296
    end
    return hash
end

local function dump_region(boundary, name, address, size)
    local output = assert(io.open(string.format("%s/%s-%s.bin", ROOT, boundary, name), "wb"))
    local bytes = {}
    for offset = 0, size - 1 do
        bytes[#bytes + 1] = string.char(space:read_u8(address + offset))
        if #bytes == 4096 then
            output:write(table.concat(bytes))
            bytes = {}
        end
    end
    if #bytes ~= 0 then output:write(table.concat(bytes)) end
    output:close()
end

local function dump_pcs(name)
    if not debug then
        log("pc_coverage", "name=" .. name .. " status=unavailable")
        return
    end
    local output = assert(io.open(string.format("%s/%s-pcs.txt", ROOT, name), "w"))
    local count = 0
    for address = 0, 0x001ffffc, 4 do
        if debug:track_pc_visited(address) then
            output:write(string.format("%08x\n", address))
            count = count + 1
        end
    end
    output:close()
    log("pc_coverage", string.format("name=%s count=%d", name, count))
end

local function snapshot(name)
    pcall(function() manager.machine.video:snapshot() end)
    log("snapshot", "name=" .. name)
end

local function capture_boundary(name)
    -- Queue tracing is a narrow diagnostic path; avoid multi-megabyte
    -- unrelated memory dumps that can delay reaching the target producer.
    if queue_trace then return end
    if phase ~= "warmup" then dump_pcs(name) end
    dump_region(name, "workram", WORKRAM_BASE, WORKRAM_BYTES)
    dump_region(name, "tilemap", TILE_BASE, TILE_BYTES)
    dump_region(name, "geometry-buffer", GEO_BUFFER_BASE, GEO_BUFFER_BYTES)
    dump_region(name, "texture-bank0", TEXTURE0_BASE, TEXTURE_BYTES)
    dump_region(name, "texture-bank1", TEXTURE1_BASE, TEXTURE_BYTES)
    snapshot(name)
end

local function set_phase(name)
    if phase ~= "warmup" then capture_boundary(phase .. "-end") end
    phase = name
    phase_start = frame
    if debug and ((not queue_trace and phase ~= "warmup") or
                  (queue_trace and phase == "match_entry")) then
        debug:track_pc(true, true)
    end
    log("phase_start", string.format("selector_steps=%d tile_hash=%08x", SELECT_STEPS, fnv_tilemap()))
    if phase ~= "warmup" then capture_boundary(name .. "-start") end
end

local function field(port, name)
    local p = manager.machine.ioport.ports[port]
    return p and p.fields[name] or nil
end

fields.coin = field(":IN0", "Coin 1")
fields.start = field(":IN0", "1 Player Start")
fields.right = field(":IN1", "P1 Left Stick/Right")
assert(fields.coin and fields.start and fields.right, "required input fields unavailable")

local function press(name, duration)
    fields[name]:set_value(1)
    pressed_until[name] = frame + duration
    log("input_press", string.format("name=%s until=%d", name, frame + duration))
end

local function release_inputs()
    for name, until_frame in pairs(pressed_until) do
        if frame >= until_frame then
            fields[name]:clear_value()
            pressed_until[name] = nil
            log("input_release", "name=" .. name)
        end
    end
end

local function finish(status)
    if phase ~= "warmup" then capture_boundary(phase .. "-end") end
    log("complete", "status=" .. status)
    if queue_trace then
        assert(queue_sample_interval > 0, "VON_CAPTURE_QUEUE_SAMPLE_INTERVAL must be positive")
        if debug then
            for pc = QUEUE_PC_BEGIN, QUEUE_PC_END, 4 do
                if debug:track_pc_visited(pc) then
                    queue_log:write(string.format("pc_visited=%08x\n", pc))
                end
            end
        end
        queue_log:write(string.format("# complete samples=%d\n", queue_samples))
        queue_log:close()
    end
    events:close()
    manager.machine:exit()
end

emu.register_periodic(function()
    frame = frame + 1
    release_inputs()

    if queue_trace and queue_samples < queue_max_samples and (frame % queue_sample_interval == 0) then
        local pc_entry = state["GENPC"] or state["CURPC"]
        local pc = pc_entry and tonumber(pc_entry.value)
        local read_index = space:read_u32(QUEUE_READ)
        local write_index = space:read_u32(QUEUE_WRITE)
        local slot = write_index % 64
        local byte = space:read_u8(QUEUE_BASE + slot)
        queue_log:write(string.format(
            "sample=%d frame=%d time=%.6f pc=%s read=%08x write=%08x slot=%02x byte=%02x\n",
            queue_samples, frame, emu.time(), pc and string.format("%08x", pc) or "unknown",
            read_index, write_index, slot, byte))
        queue_samples = queue_samples + 1
    end

    if phase == "warmup" then
        if frame >= START_TRACE_FRAME then
            set_phase("title_dwell")
            coin_frame = phase_start + TITLE_DWELL_FRAMES
            log("title_ready", string.format("frame=%d coin_frame=%d", frame, coin_frame))
        end
        return
    end

    if phase == "title_dwell" and frame >= coin_frame then
        press("coin", 8)
        set_phase("coin_insert")
        return
    end

    if phase == "coin_insert" and frame >= phase_start + 180 then
        set_phase("machine_select")
        return
    end

    if phase == "machine_select" then
        local selector_frame = phase_start + SELECT_STEPS * 45
        if next_selection_step <= SELECT_STEPS and frame >= phase_start + next_selection_step * 45 then
            press("right", 8)
            next_selection_step = next_selection_step + 1
        end
        if frame >= selector_frame + 120 then
            press("start", 8)
            set_phase("takeoff")
        end
        return
    end

    if phase == "takeoff" and frame >= phase_start + 360 then
        set_phase("level_intro")
        return
    end

    if phase == "level_intro" and frame >= phase_start + 540 then
        set_phase("match_entry")
        return
    end

    if start_frame == nil and phase == "takeoff" then start_frame = phase_start end
    if start_frame and frame >= start_frame + MAX_POST_START_FRAMES then
        finish("match_entry_timeout")
    end
end)
