-- Scripted attract-to-gameplay progression for the Virtual-On MAME driver.
--
-- Reads the confirmed 64x64 text tilemap at bus address 0x01000000 through the
-- i960 program space (tile value = 0x8000 | ASCII) and drives IN0/IN1/IN2
-- fields directly, so host keyboard mapping quirks are irrelevant.
--
-- Confirmed flow (vonj-progress traces and snapshots):
--   warning auto-dismisses, attract runs, a Coin 1 pulse at ~frame 900 opens
--   MACHINE SELECT, and 1 Player Start at ~frame 1500 confirms the highlighted
--   machine. The game then runs its brief pre-match scene before the first
--   deterministic battle (the first opponent and arena are fixed).
-- An optional combat phase can cycle stick directions and pulse both shot
-- triggers for general trace coverage; disable it when capturing the untouched
-- first-match scene with VON_PROGRESS_COMBAT=0.
--
-- Every tilemap checksum change and input press is logged. emu.print_info
-- does not reach -oslog, so we write our own log file.
-- Environment: VON_PROGRESS_SECONDS (default 150 emulated seconds)
--              VON_PROGRESS_LOG     (log file path)
--              VON_PROGRESS_COMBAT  (default 1; set 0 for passive capture)
--              VON_PROGRESS_COMBAT_START (default 1800)
--              VON_PROGRESS_SELECT_STEPS (right presses before confirmation)
--              VON_PROGRESS_AUTO_START (default 1; set 0 for selector-only capture)
--              VON_PROGRESS_GEOMETRY_STATE_LOG (optional state log path)
--              VON_PROGRESS_MOTION_SELECTOR_LOG (optional object-selector log)
--              VON_PROGRESS_MOTION_SELECTOR_PC (default 0x3454c)
--              VON_PROGRESS_SHOT_PATTERN (alternate, left, or right)
--              VON_PROGRESS_SHOT_INTERVAL (default 45 frames)
--              VON_PROGRESS_SHOT_HOLD_FRAMES (default 20)
--              VON_PROGRESS_COMBAT_END (default 7000)
--              VON_PROGRESS_ACTIVE_LEVELS (1 to use raw electrical polarity)
--              VON_PROGRESS_TRANSFORM_LOG (ordered i960/SHARC NDJSON events)

local SECONDS = tonumber(os.getenv("VON_PROGRESS_SECONDS") or "150")
local TARGET_FRAMES = SECONDS * 60
local CAPTURE_START_FRAME = tonumber(os.getenv("VON_PROGRESS_CAPTURE_START_FRAME") or "0")
local LOG_PATH = os.getenv("VON_PROGRESS_LOG") or "vonj-progress-lua.log"
local GEOMETRY_STATE_LOG_PATH = os.getenv("VON_PROGRESS_GEOMETRY_STATE_LOG")
local MOTION_SELECTOR_LOG_PATH = os.getenv("VON_PROGRESS_MOTION_SELECTOR_LOG")
local MOTION_SELECTOR_PC = tonumber(
    os.getenv("VON_PROGRESS_MOTION_SELECTOR_PC") or "0x3454c")
local MOTION_SELECTOR_MAX = tonumber(
    os.getenv("VON_PROGRESS_MOTION_SELECTOR_MAX") or "20000")
-- Optional SHARC affine-state trace: taps the copro DSP data space so the
-- 12-word matrices the services mutate/commit are observable directly, not
-- only through the geometry board's re-read.  VON_PROGRESS_SHARC_TAP_MIN/MAX
-- bound the tapped window (default the 0x1400000 commit region); the tap also
-- logs the working-matrix pointer DM(0x30101) so the push/pop base is visible.
local SHARC_LOG_PATH = os.getenv("VON_PROGRESS_SHARC_LOG")
local SHARC_FIFO_READS = os.getenv("VON_PROGRESS_SHARC_FIFO_READS") == "1"
local SHARC_FIFO_REGS = os.getenv("VON_PROGRESS_SHARC_FIFO_REGS") == "1"
local SHARC_TAP_MIN = tonumber(
    os.getenv("VON_PROGRESS_SHARC_TAP_MIN") or "0x01400000")
local SHARC_TAP_MAX = tonumber(
    os.getenv("VON_PROGRESS_SHARC_TAP_MAX") or "0x01410000")
local SHARC_MAX = tonumber(os.getenv("VON_PROGRESS_SHARC_MAX") or "40000")
local TRANSFORM_LOG_PATH = os.getenv("VON_PROGRESS_TRANSFORM_LOG")
local CAMERA_LOG_PATH = os.getenv("VON_PROGRESS_CAMERA_LOG")
local ACTIVE_LEVELS = os.getenv("VON_PROGRESS_ACTIVE_LEVELS") == "1"
local RAM_SNAP_FRAME = tonumber(os.getenv("VON_PROGRESS_RAM_SNAP_FRAME") or "0")
local RAM_SNAP_PATH = os.getenv("VON_PROGRESS_RAM_SNAP_PATH")
local RAM_SNAP_BASE = tonumber(os.getenv("VON_PROGRESS_RAM_SNAP_BASE") or "0x00500000")
local RAM_SNAP_LEN = tonumber(os.getenv("VON_PROGRESS_RAM_SNAP_LEN") or "4096")

local TILE_BASE = 0x01000000
local ROWS = 64
local COLS = 64

local log_file = assert(io.open(LOG_PATH, "w"))
log_file:write("progress: session start\n")
log_file:flush()

-- Per-frame camera extrinsics, so a transform capture can be converted from
-- camera-relative space back to model space (recovered-camera.md cells).
local camera_file
if CAMERA_LOG_PATH then
    camera_file = assert(io.open(CAMERA_LOG_PATH, "w"))
    camera_file:write("camera: session start\n")
    camera_file:flush()
end

local geometry_state_file
if GEOMETRY_STATE_LOG_PATH then
    geometry_state_file = assert(io.open(GEOMETRY_STATE_LOG_PATH, "w"))
    geometry_state_file:write("geometry-state: session start\n")
    geometry_state_file:flush()
end

-- The animation selector's active-header load executes at 0x3454c.  At this
-- point r8 is the object base, while the read is the published header global
-- 0x51ab08.  r8 is re-used before the later copro-FIFO writes, so this
-- program-space read tap is deliberately at the load, not at the FIFO port.
-- Lua exposes both the i960 state entries and address-space taps, letting a
-- normal autoboot capture establish the object->selector relation without a
-- MAME source rebuild.
local motion_selector_file
local motion_selector_tap
local motion_selector_cpu
local motion_selector_events = 0
local motion_selector_reading = false
-- Declare these before the closure so it captures the script's live state,
-- rather than resolving an accidental global named `space`.
local frame = 0
local space

-- One monotonically ordered stream shared by the i960 FIFO, selector, and
-- SHARC stack/commit taps. Callback order, rather than emulated timestamps,
-- is the join key used by normalize/analyze tooling.
local transform_file
local transform_event_id = 0
local function transform_event(kind, body)
    if not transform_file then
        return
    end
    transform_event_id = transform_event_id + 1
    transform_file:write(string.format(
        '{"event_id":%d,"kind":"%s","frame":%d%s}\n',
        transform_event_id, kind, frame, body or ""))
    transform_file:flush()
end

local function install_motion_selector_tap()
    if (not MOTION_SELECTOR_LOG_PATH and not transform_file) or
            motion_selector_tap or not space then
        return
    end
    motion_selector_cpu = manager.machine.devices[":maincpu"]
    if not motion_selector_cpu then
        return
    end
    if MOTION_SELECTOR_LOG_PATH then
        motion_selector_file = assert(io.open(MOTION_SELECTOR_LOG_PATH, "w"))
    end
    if motion_selector_file then
        motion_selector_file:write(string.format(
            "motion-selector: pc=%08x source=lua-program-read-tap\n",
            MOTION_SELECTOR_PC))
        motion_selector_file:flush()
    end
    -- The selector consumer is in this small published-header block.  A
    -- 16-byte tap is required for MAME's mapped 32-bit bus handler while
    -- avoiding an otherwise expensive callback on every work-RAM read.
    motion_selector_tap = space:install_read_tap(
        0x0051ab00, 0x0051ab0f, "von-motion-selector",
        function(address, data, mem_mask)
            if motion_selector_reading or motion_selector_events >= MOTION_SELECTOR_MAX then
                return
            end
            -- i960 exposes the active instruction address as CURPC (not the
            -- display-only PC alias used by several other CPU cores).
            local pc_entry = motion_selector_cpu.state["CURPC"]
            local r8_entry = motion_selector_cpu.state["r8"]
            local g0_entry = motion_selector_cpu.state["g0"]
            if not pc_entry or not r8_entry or not g0_entry then
                return
            end
            local pc = tonumber(pc_entry.value)
            local object = tonumber(r8_entry.value)
            local selector_object = tonumber(g0_entry.value)
            if pc ~= MOTION_SELECTOR_PC then
                return
            end
            -- A broad range reports an absolute address while a local block
            -- reports its byte offset.  The base header is offset +8.
            if object < 0x00500000 or object > 0x005fffff
                or selector_object < 0x00500000 or selector_object > 0x005fffff
                or (address ~= 0x0051ab08 and address ~= 8) then
                return
            end
            motion_selector_reading = true
            local ok, selector, state, cursor, body_header = pcall(function()
                return space:read_u16(selector_object + 0x174),
                    space:read_u16(selector_object + 0x176),
                    space:read_u16(selector_object + 0x17a),
                    space:read_u32(0x0051ab0c)
            end)
            motion_selector_reading = false
            if not ok then
                return
            end
            motion_selector_events = motion_selector_events + 1
            transform_event("motion_selector", string.format(
                ',"pc":%d,"object":%d,"selector_object":%d,' ..
                '"skeleton_header":%d,"body_header":%d,' ..
                '"selector":%d,"state":%d,"cursor":%d',
                pc, object, selector_object, data, body_header,
                selector, state, cursor))
            if motion_selector_file then
                motion_selector_file:write(string.format(
                    "motion-selector: frame=%d object=%08x g0=%08x header=%08x body_header=%08x sel=%04x state=%04x frame_cursor=%04x\n",
                    frame, object, selector_object, data, body_header, selector, state, cursor))
                motion_selector_file:flush()
            end
        end)
end

-- Raw SHARC affine-state tap.  The recovered service handlers keep the
-- working 12-word matrix behind the pointer at DM(0x30101) and commit it to
-- `0x01400000 + (word >> 2)`; service 0x05/0x06 push/pop a copy so a child's
-- base is the parent state.  Reading the committed words in place settles
-- whether the board matrix is the cumulative world or the local record,
-- without inferring it from the geometry parser.
local sharc_file
local sharc_tap
local sharc_device
local sharc_space
local sharc_writes = 0
local sharc_reading = false
local sharc_stack_tap
local sharc_fifo_read_tap
local sharc_live_words
local sharc_reg_pending_command
local i960_fifo_tap
local marker_slot_tap
local marker_slot_read_tap
local marker_slot_reading = false
local marker_slot_words = {}
local sharc_last_depth = 0
local sharc_pending_stack_kind
local commit_run = { start = nil, next = nil, words = {} }

local function state_value(device, name)
    local entry = device and device.state and device.state[name]
    return entry and tonumber(entry.value) or 0
end

local function matrix_at(address)
    local words = {}
    for i = 0, 11 do
        local ok, word = pcall(function()
            return sharc_space:read_u32(address + i)
        end)
        words[#words + 1] = ok and word or 0xffffffff
    end
    return words
end

local function json_words(words)
    local out = {}
    for _, word in ipairs(words) do
        out[#out + 1] = tostring(word)
    end
    return "[" .. table.concat(out, ",") .. "]"
end

local function flush_commit_run()
    -- Services 0x39/0x3a/0x3b write a 13-word geometry record: a fixed
    -- 0x05800b0b seed followed by the committed row-major 3x4 matrix.
    if #commit_run.words == 13 and commit_run.words[1] == 0x05800b0b then
        local matrix = {}
        for i = 2, 13 do
            matrix[#matrix + 1] = commit_run.words[i]
        end
        transform_event("commit", string.format(
            ',"pc":%d,"depth":%d,"destination":"0x%08x",' ..
            '"matrix_words":%s,"stack_words":%s',
            state_value(sharc_device, "CURPC"), sharc_last_depth,
            commit_run.start, json_words(matrix),
            json_words(commit_run.stack_words or {})))
    elseif #commit_run.words > 0 then
        transform_event("commit_fragment", string.format(
            ',"destination":"0x%08x","word_count":%d',
            commit_run.start, #commit_run.words))
    end
    commit_run = { start = nil, next = nil, words = {} }
end

local function install_i960_fifo_tap()
    if not transform_file or i960_fifo_tap or not space or not motion_selector_cpu then
        return
    end
    i960_fifo_tap = space:install_write_tap(
        0x00884000, 0x00884003, "von-transform-fifo",
        function(offset, data, mask)
            transform_event("i960_fifo", string.format(
                ',"pc":%d,"data":%d,"mask":%d,"r6":%d,' ..
                '"g0":%d,"g2":%d,"g4":%d',
                state_value(motion_selector_cpu, "CURPC"), data, mask,
                state_value(motion_selector_cpu, "r6"),
                state_value(motion_selector_cpu, "g0"),
                state_value(motion_selector_cpu, "g2"),
                state_value(motion_selector_cpu, "g4")))
            return data
        end)
end

local function install_marker_slot_tap()
    if not transform_file or marker_slot_tap or not space or
            not motion_selector_cpu then
        return
    end
    marker_slot_tap = space:install_write_tap(
        0x00562430, 0x00562477, "von-transform-marker-slots",
        function(offset, data, mask)
            local relative = offset - 0x00562430
            local slot = math.floor(relative / 12)
            local field = math.floor((relative % 12) / 4)
            if marker_slot_words[slot] == nil then
                marker_slot_words[slot] = { 0, 0, 0 }
            end
            marker_slot_words[slot][field + 1] = data
            transform_event("marker_slot_write", string.format(
                ',"pc":%d,"address":%d,"slot":%d,"field":%d,' ..
                '"data":%d,"mask":%d',
                state_value(motion_selector_cpu, "CURPC"), offset,
                slot, field,
                data, mask))
            return data
        end)
    marker_slot_read_tap = space:install_read_tap(
        0x00562430, 0x00562477, "von-transform-marker-slot-consume",
        function(offset, data, mask)
            if marker_slot_reading then
                return data
            end
            marker_slot_reading = true
            local relative = offset - 0x00562430
            local slot = math.floor(relative / 12)
            local field = math.floor((relative % 12) / 4)
            local words = marker_slot_words[slot] or { 0, 0, 0 }
            -- Log the complete producer state at the read, not just one field:
            -- a marker source is an ordered slot consumption, and a later
            -- sibling rewrite must not be retroactively attributed to it.
            transform_event("marker_slot_consume", string.format(
                ',"pc":%d,"address":%d,"slot":%d,"field":%d,' ..
                '"data":%d,"mask":%d,"slot_words":%s,' ..
                '"r6":%d,"g0":%d,"g1":%d,"g2":%d,"g3":%d,"g4":%d,"g5":%d',
                state_value(motion_selector_cpu, "CURPC"), offset, slot, field,
                data, mask, json_words(words),
                state_value(motion_selector_cpu, "r6"),
                state_value(motion_selector_cpu, "g0"),
                state_value(motion_selector_cpu, "g1"),
                state_value(motion_selector_cpu, "g2"),
                state_value(motion_selector_cpu, "g3"),
                state_value(motion_selector_cpu, "g4"),
                state_value(motion_selector_cpu, "g5")))
            marker_slot_reading = false
            return data
        end)
end

local function find_sharc()
    for _, dev in pairs(manager.machine.devices) do
        if dev.shortname == "adsp21062" then
            return dev
        end
    end
    return manager.machine.devices[":copro"]
end

local function install_sharc_tap()
    if (not SHARC_LOG_PATH and not transform_file and not SHARC_FIFO_READS) or sharc_tap then
        return
    end
    sharc_device = find_sharc()
    if not sharc_device then
        return
    end
    sharc_space = sharc_device.spaces[":data"] or sharc_device.spaces["data"]
        or sharc_device.spaces[":program"] or sharc_device.spaces["program"]
    if not sharc_space then
        return
    end
    if SHARC_LOG_PATH then
        sharc_file = assert(io.open(SHARC_LOG_PATH, "w"))
        sharc_file:write(string.format(
            "sharc-state: tap=[%08x,%08x] device=%s\n",
            SHARC_TAP_MIN, SHARC_TAP_MAX, tostring(sharc_device.shortname)))
        sharc_file:flush()
    end
    local ok, err = pcall(function()
        sharc_tap = sharc_space:install_write_tap(
            SHARC_TAP_MIN, SHARC_TAP_MAX, "von-sharc-state",
            function(offset, data, mask)
                -- SHARC_MAX is the historical human-readable log cap. The
                -- ordered evidence stream must not silently stop mid-run.
                if sharc_reading or
                        (not transform_file and sharc_writes >= SHARC_MAX) then
                    return data
                end
                sharc_reading = true
                sharc_writes = sharc_writes + 1
                local ptr = 0
                pcall(function()
                    ptr = sharc_space:read_u32(0x0030101)
                end)
                if sharc_file then
                    sharc_file:write(string.format(
                        "sharc-write: frame=%d offset=%08x data=%08x mask=%08x ptr=%08x\n",
                        frame, offset, data, mask, ptr))
                    sharc_file:flush()
                end
                if transform_file then
                    if commit_run.start == nil then
                        commit_run.start = offset
                        commit_run.next = offset
                        -- The geometry commit is produced from the live
                        -- stack matrix. Capture that source before any
                        -- destination writes so offline replay can separate
                        -- fighter-local services from object/world factoring.
                        local ptr_ok, ptr = pcall(function()
                            return sharc_space:read_u32(0x0030101)
                        end)
                        if ptr_ok then
                            commit_run.stack_words = matrix_at(ptr)
                        end
                    elseif offset ~= commit_run.next then
                        flush_commit_run()
                        commit_run.start = offset
                        commit_run.next = offset
                    end
                    commit_run.words[#commit_run.words + 1] = data
                    commit_run.next = offset + 1
                    if #commit_run.words == 13 then
                        flush_commit_run()
                    end
                end
                sharc_reading = false
                return data
            end)
    end)
    if not ok then
        if sharc_file then
            sharc_file:write("sharc-state: install failed: " .. tostring(err) .. "\n")
            sharc_file:flush()
        end
        transform_event("tap_error", ',"tap":"sharc_commit"')
    end

    if transform_file then
        -- Stack bookkeeping and the copied 12-word windows are disjoint from
        -- the commit destination range, so use a second Lua tap. A pointer
        -- write is the ordered point at which the pushed/restored base can be
        -- read exactly from the copied window.
        local stack_ok, stack_err = pcall(function()
            sharc_stack_tap = sharc_space:install_write_tap(
                0x0030100, 0x0030260, "von-transform-stack",
                function(offset, data, mask)
                    if sharc_reading then
                        return data
                    end
                    sharc_reading = true
                    local pc = state_value(sharc_device, "CURPC")
                    if offset == 0x0030100 then
                        if data > sharc_last_depth then
                            sharc_pending_stack_kind = "push"
                        elseif data < sharc_last_depth then
                            sharc_pending_stack_kind = "pop"
                        else
                            sharc_pending_stack_kind = "reset"
                        end
                        sharc_last_depth = data
                    elseif offset == 0x0030101 then
                        local words = matrix_at(data)
                        local kind = sharc_pending_stack_kind or "stack_pointer"
                        local depth = sharc_last_depth
                        local matrix_field = "matrix_words"
                        local suffix = ""
                        if kind == "push" then
                            matrix_field = "base_words"
                        elseif kind == "pop" then
                            -- The handler stores the decremented depth before
                            -- its restored pointer. Preserve both sides of the
                            -- operation; lineage consumes the pre-pop depth.
                            depth = sharc_last_depth + 1
                            matrix_field = "restored_words"
                            suffix = string.format(',"depth_after":%d',
                                sharc_last_depth)
                        end
                        transform_event(kind,
                            string.format(',"pc":%d,"depth":%d%s,' ..
                                '"pointer":%d,"%s":%s', pc, depth, suffix,
                                data, matrix_field, json_words(words)))
                        sharc_pending_stack_kind = nil
                    elseif offset >= 0x003010c and offset < 0x0030260 then
                        -- The stack tap already records pointer changes, but
                        -- SHARC services can mutate the live matrix in place
                        -- while a frame remains pushed. Preserve those writes
                        -- so lineage can identify the service between sibling
                        -- pushes instead of treating the changed base as a
                        -- fitted parent.
                        local reg_suffix = ""
                        if SHARC_FIFO_REGS and (pc == 131876 or pc == 131904 or
                                pc == 131848 or pc == 132877) then
                            reg_suffix = string.format(
                                ',"r0":%d,"r1":%d,"r2":%d,"r3":%d,"r4":%d,"r5":%d,"r6":%d,"r7":%d,"r8":%d,"r9":%d,"r10":%d,"r11":%d,"r12":%d,"r13":%d,"r14":%d,"r15":%d',
                                state_value(sharc_device, "R0"), state_value(sharc_device, "R1"),
                                state_value(sharc_device, "R2"), state_value(sharc_device, "R3"),
                                state_value(sharc_device, "R4"), state_value(sharc_device, "R5"),
                                state_value(sharc_device, "R6"), state_value(sharc_device, "R7"),
                                state_value(sharc_device, "R8"), state_value(sharc_device, "R9"),
                                state_value(sharc_device, "R10"), state_value(sharc_device, "R11"),
                                state_value(sharc_device, "R12"), state_value(sharc_device, "R13"),
                                state_value(sharc_device, "R14"), state_value(sharc_device, "R15"))
                        end
                        local ptr_ok, ptr = pcall(function()
                            return sharc_space:read_u32(0x0030101)
                        end)
                        transform_event("sharc_service_write",
                            string.format(',"pc":%d,"depth":%d,"offset":%d,"data":%d,"mask":%d,"pointer":%d%s',
                                pc, sharc_last_depth, offset, data, mask,
                                ptr_ok and ptr or 0, reg_suffix))
                        if ptr_ok then
                            sharc_live_words = matrix_at(ptr)
                        end
                    end
                    sharc_reading = false
                    return data
                end)
        end)
        if not stack_ok then
            transform_event("tap_error", ',"tap":"sharc_stack"')
            if sharc_file then
                sharc_file:write("sharc-state: stack tap failed: " ..
                    tostring(stack_err) .. "\n")
            end
        end
    end

    if SHARC_FIFO_READS and transform_file then
        pcall(function()
            -- model2b::copro_sharc_map maps the i960 input FIFO to the
            -- SHARC data-space window 0x0400000..0x0bfffff.  The firmware
            -- consumes the stream through the first word of that window.
            sharc_fifo_read_tap = sharc_space:install_read_tap(
                0x00400000, 0x00400003, "von-transform-sharc-fifo-read",
                function(offset, data, mask)
                    local pc = state_value(sharc_device, "PC")
                    local suffix = ""
                    if SHARC_FIFO_REGS and (data == 20 or data == 21 or
                            data == 22 or data == 58 or
                            sharc_reg_pending_command ~= nil) then
                        suffix = string.format(
                            ',"registers_for":%d,"r0":%d,"r1":%d,"r2":%d,"r3":%d,"r4":%d,"r5":%d,"r6":%d,"r7":%d,"r8":%d,"r9":%d,"r10":%d,"r11":%d,"r12":%d,"r13":%d,"r14":%d,"r15":%d',
                            sharc_reg_pending_command or data,
                            state_value(sharc_device, "R0"), state_value(sharc_device, "R1"),
                            state_value(sharc_device, "R2"), state_value(sharc_device, "R3"),
                            state_value(sharc_device, "R4"), state_value(sharc_device, "R5"),
                            state_value(sharc_device, "R6"), state_value(sharc_device, "R7"),
                            state_value(sharc_device, "R8"), state_value(sharc_device, "R9"),
                            state_value(sharc_device, "R10"), state_value(sharc_device, "R11"),
                            state_value(sharc_device, "R12"), state_value(sharc_device, "R13"),
                            state_value(sharc_device, "R14"), state_value(sharc_device, "R15"))
                    end
                    if data == 20 or data == 21 or data == 22 then
                        sharc_reg_pending_command = data
                    else
                        sharc_reg_pending_command = nil
                    end
                    transform_event("sharc_fifo_read", string.format(
                        ',"pc":%d,"offset":%d,"data":%d,"mask":%d%s',
                        pc, offset, data, mask, suffix))
                    -- Opcode 0x3a (word 58) terminates a transform service.
                    -- At this read the service's source pointer still names
                    -- the live fighter-local matrix; capture it before the
                    -- commit handler advances or factors the object matrix.
                    if data == 58 then
                        local ok, ptr = pcall(function()
                            return sharc_space:read_u32(0x0030101)
                        end)
                        if ok then
                            transform_event("sharc_service_source",
                                string.format(',"pc":%d,"pointer":%d,"matrix_words":%s',
                                    pc, ptr, json_words(sharc_live_words or matrix_at(ptr))))
                        end
                    end
                    return data
                end)
        end)
    end
end

local function log(message)
    log_file:write(message .. "\n")
    log_file:flush()
end

local function log_geometry_state(message)
    if geometry_state_file then
        geometry_state_file:write(message .. "\n")
        geometry_state_file:flush()
    end
end

local fields = {}
local SNAPSHOT_FRAME = tonumber(os.getenv("VON_PROGRESS_RAM_SNAPSHOT") or "0")
local SNAPSHOT_PATH = os.getenv("VON_PROGRESS_RAM_SNAPSHOT_PATH")
local snapshot_done = false

local function ram_snapshot()
    if snapshot_done or not space or not SNAPSHOT_PATH then
        return
    end
    snapshot_done = true
    local out = assert(io.open(SNAPSHOT_PATH, "w"))
    for address = 0x00500000, 0x005fffff, 4 do
        local ok, value = pcall(function() return space:read_u32(address) end)
        if ok then
            out:write(string.format("%08x %08x\n", address, value))
        end
        if address % 0x10000 == 0 then
            out:flush()
        end
    end
    out:close()
    log("progress: ram snapshot written")
end
local last_screen_hash = nil
local pressed_until = {}
local last_geometry_state

local function geometry_state()
    if not space or not geometry_state_file then
        return
    end
    local function read_word(address)
        local ok, value = pcall(function() return space:read_u32(address) end)
        if ok then
            return value
        end
        return 0xffffffff
    end
    local function read_byte(address)
        local ok, value = pcall(function() return space:read_u8(address) end)
        if ok then
            return value
        end
        return 0xff
    end
    -- These are the host-side state words consumed by 0x6f6f0 after its
    -- opcode-0x41 lookup: mode, callback byte-map base, selected record
    -- table, alternate record field, and the two output mask globals.
    local values = {
        mode = space:read_u32(0x005770f0),
        byte_map = space:read_u32(0x0051bb20),
        records = space:read_u32(0x0051bb24),
        record_aux = space:read_u32(0x0051bb28),
        mask_special = space:read_u32(0x00562c80),
        mask_general = space:read_u32(0x00562c84),
    }
    local record_words = {}
    for _, selector in ipairs({ 0, 6, 13 }) do
        local base = values.records + selector * 20
        local words = {}
        for offset = 0, 16, 4 do
            words[#words + 1] = read_word(base + offset)
        end
        record_words[#record_words + 1] = string.format(
            "%d:%08x,%08x,%08x,%08x,%08x", selector,
            words[1], words[2], words[3], words[4], words[5])
    end
    local map_bytes = {}
    for offset = 0, 31 do
        map_bytes[#map_bytes + 1] = string.format(
            "%02x", read_byte(values.byte_map + offset))
    end
    local state = string.format(
        "%08x/%08x/%08x/%08x/%08x/%08x/%s/%s",
        values.mode, values.byte_map, values.records, values.record_aux,
        values.mask_special, values.mask_general,
        table.concat(record_words, "/"), table.concat(map_bytes))
    if state ~= last_geometry_state then
        log_geometry_state(string.format(
            "geometry-state: frame %d mode=%08x byte_map=%08x records=%08x " ..
            "record_aux=%08x mask_special=%08x mask_general=%08x " ..
            "records012: %s map[0:32]=%s",
            frame, values.mode, values.byte_map, values.records,
            values.record_aux, values.mask_special, values.mask_general,
            table.concat(record_words, "/"), table.concat(map_bytes)))
        last_geometry_state = state
    end
end

-- M2 live upload-cluster observer: the reconstructed image runs one
-- 768-store direct-path pass at startup (counter preset 4, fade 0x80,
-- mode 0) and records stores, post-run counter, and two destination
-- words at WORKRAM+0x20 slots 12..15. Sampled source words let the
-- analyst check dst == scale(src) for the run. Change-triggered.
local last_upload_state = nil

local function upload_state()
    if not space or not geometry_state_file then
        return
    end
    local function read_word(address)
        local ok, value = pcall(function() return space:read_u32(address) end)
        if ok then
            return value
        end
        return 0xffffffff
    end
    local stores = read_word(0x00500050)
    local counter = read_word(0x00500054)
    local dst_first = read_word(0x00500058)
    local dst_last = read_word(0x0050005c)
    local src_first = read_word(0x01814100)
    local src_last = read_word(0x01814e7c)
    local dst_first_live = read_word(0x01814000)
    local dst_last_live = read_word(0x01814e7c)
    local state = string.format(
        "%08x/%08x/%08x/%08x/%08x/%08x/%08x/%08x",
        stores, counter, dst_first, dst_last,
        src_first, src_last, dst_first_live, dst_last_live)
    if state ~= last_upload_state then
        log_geometry_state(string.format(
            "upload-state: frame %d stores=%08x counter=%08x " ..
            "dst_first=%08x dst_last=%08x src_first=%08x src_last=%08x " ..
            "live_first=%08x live_last=%08x",
            frame, stores, counter, dst_first, dst_last,
            src_first, src_last, dst_first_live, dst_last_live))
        last_upload_state = state
    end
end

-- Confirmed field names on the vonj driver (IN0/IN1/IN2).
local FIELD_NAMES = {
    coin       = { ":IN0", "Coin 1" },
    start      = { ":IN0", "1 Player Start" },
    down       = { ":IN1", "P1 Left Stick/Down" },
    up         = { ":IN1", "P1 Left Stick/Up" },
    right      = { ":IN1", "P1 Left Stick/Right" },
    left       = { ":IN1", "P1 Left Stick/Left" },
    left_shot  = { ":IN1", "P1 Left Shot" },
    left_dash  = { ":IN1", "P1 Left Dash" },
    right_shot = { ":IN2", "P1 Right Shot" },
    right_dash = { ":IN2", "P1 Right Dash" },
}

local function setup()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then
        return false
    end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    if not space then
        log("progress: no program space")
        return false
    end
    motion_selector_cpu = cpu
    if TRANSFORM_LOG_PATH then
        transform_file = assert(io.open(TRANSFORM_LOG_PATH, "w"))
        transform_event("session", ',"schema_version":1')
    end
    for key, spec in pairs(FIELD_NAMES) do
        local port = manager.machine.ioport.ports[spec[1]]
        fields[key] = port and port.fields[spec[2]] or nil
    end
    for _, key in ipairs({ "coin", "start", "left_shot" }) do
        if not fields[key] then
            log("progress: missing required field " .. key)
            return false
        end
    end
    for key, _ in pairs(FIELD_NAMES) do
        if not fields[key] then
            log("progress: missing optional field " .. key)
        end
    end
    log("progress: fields resolved")
    local tap_addr = tonumber(os.getenv("VON_MEM_TAP_ADDR") or "0")
    local tap_count = tonumber(os.getenv("VON_MEM_TAP_COUNT") or "8")
    if tap_addr > 0 then
        local cpu = manager.machine.devices[":maincpu"]
        if os.getenv("VON_MEM_TAP_DEBUG") then
            local probes = {
                ["colon-PC"] = function() return cpu:state("PC") end,
                ["colon-0"] = function() return cpu:state(0) end,
                ["bracket-pc"] = function() return cpu.state["pc"].value end,
            }
            for name, fn in pairs(probes) do
                local ok, res = pcall(fn)
                local info = ok and type(res) or "ERR"
                local val = ""
                if ok and type(res) == "table" then
                    local okv, v = pcall(function() return res.value end)
                    val = okv and (" value=" .. tostring(v)) or ""
                elseif ok then
                    val = " =" .. tostring(res)
                end
                log(string.format("progress: cpustate %s: %s%s", name,
                    info, val))
            end
        end
        local hits = 0
        local tap
        tap = space:install_read_tap(tap_addr, tap_addr + 3, "selwatch",
            function(offset, data, mask)
                hits = hits + 1
                local pc = "?"
                local ok, st = pcall(function()
                    return cpu.state["CURPC"].value
                end)
                if ok and type(st) == "number" then
                    pc = string.format("0x%x", st)
                end
                log(string.format(
                    "progress: memtap hit %d addr=0x%x pc=%s frame=%d",
                    hits, tap_addr, pc, frame))
                if hits >= tap_count and tap then
                    space:uninstall_read_tap(tap)
                    log("progress: memtap removed")
                end
                return data
            end)
        log(string.format("progress: memtap installed at 0x%x", tap_addr))
    end
    if MOTION_SELECTOR_LOG_PATH then
        log("progress: motion-selector log " .. MOTION_SELECTOR_LOG_PATH)
    end
    install_motion_selector_tap()
    install_i960_fifo_tap()
    install_marker_slot_tap()
    if SHARC_LOG_PATH then
        log("progress: sharc-state log " .. SHARC_LOG_PATH)
    end
    install_sharc_tap()
    return true
end

local function press(key, until_frame)
    local f = fields[key]
    if not f then
        return
    end
    pressed_until[key] = until_frame
    -- MAME's Lua override is logical by default: the verified input mapper
    -- and battle sandbox use 1/clear_value regardless of port polarity.
    if not ACTIVE_LEVELS then
        f:set_value(1)
        return
    end
    local mask = f.mask or 1
    local def = f.defvalue or mask
    local inactive = def & mask
    local active = inactive == 0 and mask or 0
    f:set_value(active)
end

local function release_expired()
    for key, until_frame in pairs(pressed_until) do
        if frame >= until_frame then
            local f = fields[key]
            if f then
                f:clear_value()
            end
            pressed_until[key] = nil
        end
    end
end

local function screen_text()
    -- Decode printable 0x8000-flagged tiles into trimmed rows.
    local rows = {}
    for row = 0, ROWS - 1 do
        local chars = {}
        local base = TILE_BASE + row * COLS * 2
        for col = 0, COLS - 1 do
            local v = space:read_u16(base + col * 2)
            local c = v & 0x7fff
            if (v & 0x8000) ~= 0 and c >= 0x20 and c < 0x7f then
                chars[#chars + 1] = string.char(c)
            else
                chars[#chars + 1] = " "
            end
        end
        rows[#rows + 1] = table.concat(chars):gsub("%s+$", "")
    end
    return table.concat(rows, "\n")
end

local function tile_checksum()
    -- Whole-tilemap FNV-1a; detects graphics-only screen changes that the
    -- ASCII text decoder cannot see.
    local hash = 2166136261
    for i = 0, ROWS * COLS - 1 do
        local v = space:read_u16(TILE_BASE + i * 2)
        hash = (hash ~ v) * 16777619 % 4294967296
    end
    return hash
end

-- Boot inputs. Defaults preserve the confirmed flow; delayed captures can hold
-- the attract screen until a requested frame before injecting coin/start.
local SELECT_STEPS = tonumber(os.getenv("VON_PROGRESS_SELECT_STEPS") or "0")
local STEP_FRAMES = tonumber(os.getenv("VON_PROGRESS_STEP_FRAMES") or "45")
local AUTO_START = os.getenv("VON_PROGRESS_AUTO_START") ~= "0"
local COIN_FRAME = tonumber(os.getenv("VON_PROGRESS_COIN_FRAME") or "900")
local START_FRAME = tonumber(os.getenv("VON_PROGRESS_START_FRAME") or "1500")
local schedule = { { frame = COIN_FRAME, key = "coin" } }
for step = 1, SELECT_STEPS do
    schedule[#schedule + 1] = { frame = START_FRAME - 420 + step * STEP_FRAMES, key = "right" }
end
if AUTO_START then
    schedule[#schedule + 1] = { frame = START_FRAME + SELECT_STEPS * STEP_FRAMES, key = "start" }
end
-- Late select navigation: cursor moves after the select screen opens
-- (post-start), then an optional second start press confirms.
local LATE_STEPS = tonumber(os.getenv("VON_PROGRESS_SELECT_LATE_STEPS") or "0")
local LATE_KEY = os.getenv("VON_PROGRESS_SELECT_LATE_KEY") or "right"
local LATE_AT = tonumber(os.getenv("VON_PROGRESS_SELECT_AT") or tostring(START_FRAME))
for step = 1, LATE_STEPS do
    schedule[#schedule + 1] = { frame = LATE_AT + step * 45, key = LATE_KEY }
end
local CONFIRM_FRAME = tonumber(os.getenv("VON_PROGRESS_CONFIRM_FRAME") or "0")
local CONFIRM_KEY = os.getenv("VON_PROGRESS_CONFIRM_KEY") or "start"
if CONFIRM_FRAME > 0 then
    schedule[#schedule + 1] = { frame = CONFIRM_FRAME, key = CONFIRM_KEY }
end
local CONFIRM_COUNT = tonumber(os.getenv("VON_PROGRESS_CONFIRM_COUNT") or "0")
for step = 1, CONFIRM_COUNT do
    schedule[#schedule + 1] = {
        frame = CONFIRM_FRAME + step * 45, key = CONFIRM_KEY,
    }
end
local HOLD_FRAMES = tonumber(os.getenv("VON_PROGRESS_HOLD_FRAMES") or "8")
local schedule_index = 1

-- Combat phase: cycle the left stick around the compass and pulse both shot
-- triggers so movement, targeting, and weapon code paths all execute.
local COMBAT_ENABLED = os.getenv("VON_PROGRESS_COMBAT") ~= "0"
local COMBAT_START = tonumber(os.getenv("VON_PROGRESS_COMBAT_START") or "1800")
local COMBAT_END = tonumber(os.getenv("VON_PROGRESS_COMBAT_END") or "7000")
local DIRECTIONS = { "up", "right", "down", "left" }
local SHOT_PATTERN = os.getenv("VON_PROGRESS_SHOT_PATTERN") or "alternate"
local SHOT_INTERVAL = tonumber(os.getenv("VON_PROGRESS_SHOT_INTERVAL") or "45")
local SHOT_HOLD_FRAMES = tonumber(os.getenv("VON_PROGRESS_SHOT_HOLD_FRAMES") or "20")

local function camera_now()
    local ok, t = pcall(function() return manager.machine.time:as_double() end)
    if ok and type(t) == "number" then return t end
    return frame / 60.0
end

local function read_f32(addr)
    local ok, v = pcall(function() return space:read_u32(addr) end)
    if not ok then return 0.0 end
    return (string.unpack("<f", string.pack("<I", v)))
end

local function log_camera()
    if not camera_file or not space then return end
    local ex = read_f32(0x00504b98)
    local ey = read_f32(0x00504b9c)
    local ez = read_f32(0x00504ba0)
    local tx = read_f32(0x00504bb4)
    local ty = read_f32(0x00504bb8)
    local tz = read_f32(0x00504bbc)
    local dist = read_f32(0x00504bc8)
    camera_file:write(string.format(
        "camera: t=%.6f frame=%d eye=%.6f,%.6f,%.6f target=%.6f,%.6f,%.6f dist=%.6f\n",
        camera_now(), frame, ex, ey, ez, tx, ty, tz, dist))
    camera_file:flush()
end

emu.register_periodic(function()
    frame = frame + 1
    if not space and frame % 60 == 1 then
        if not setup() then
            return
        end
    end
    if not space or not fields.coin then
        return
    end

    release_expired()
    log_camera()

    -- Comma-separated explicit snapshot frames
    -- (VON_PROGRESS_RAM_SNAP_FRAMES="1300,1400,1500"); falls back to the
    -- legacy single-frame-plus-400s window when unset.
    local snap_suffix = nil
    if RAM_SNAP_PATH then
        local frames_raw = os.getenv("VON_PROGRESS_RAM_SNAP_FRAMES")
        if frames_raw then
            for tok in string.gmatch(frames_raw, "([^,]+)") do
                if frame == tonumber(tok) then
                    snap_suffix = string.format("-%d", frame)
                end
            end
        elseif RAM_SNAP_FRAME > 0
            and frame >= RAM_SNAP_FRAME and frame % 400 == 0
            and frame <= RAM_SNAP_FRAME + 1600 then
            snap_suffix = string.format("-%d", frame)
        end
    end
    if snap_suffix then
        local out = io.open(RAM_SNAP_PATH .. snap_suffix .. ".txt", "w")
        if out then
            for addr = RAM_SNAP_BASE, RAM_SNAP_BASE + RAM_SNAP_LEN - 1, 16 do
                local row = { string.format("%08x:", addr) }
                for off = 0, 15 do
                    local ok, v = pcall(function()
                        return space:read_u8(addr + off)
                    end)
                    row[#row + 1] = ok and string.format(" %02x", v) or " ??"
                end
                out:write(table.concat(row) .. "\n")
            end
            out:close()
            log(string.format("progress: ram snapshot frame %d -> %s", frame,
                RAM_SNAP_PATH))
        end
    end

    while schedule_index <= #schedule and frame >= schedule[schedule_index].frame do
        local step = schedule[schedule_index]
        log(string.format("progress: frame %d press %s", frame, step.key))
        if step.key == "start" then
            log("progress: machine selection confirmed; pre-match scene begins")
        end
        press(step.key, frame + (HOLD_FRAMES))
        schedule_index = schedule_index + 1
    end

    -- Input may establish the requested checkpoint before evidence begins.
    -- This lets a run press START on machine select and capture only the
    -- resulting takeoff/intro/match transition.
    if frame < CAPTURE_START_FRAME then
        return
    end

    if COMBAT_ENABLED and frame >= COMBAT_START and frame <= COMBAT_END then
        -- Change held direction every 120 frames.
        if frame % 120 == 0 then
            local key = DIRECTIONS[(math.floor(frame / 120) % #DIRECTIONS) + 1]
            log(string.format("progress: frame %d move %s", frame, key))
            press(key, frame + 120)
        end
        -- Pulse dashes every 180 frames and shots at a configurable cadence.
        if frame % 180 == 0 then
            local key = (math.floor(frame / 180) % 2) == 0 and "left_dash"
                or "right_dash"
            press(key, frame + 10)
        end
        if SHOT_INTERVAL > 0 and frame % SHOT_INTERVAL == 0 then
            local key
            if SHOT_PATTERN == "left" then
                key = "left_shot"
            elseif SHOT_PATTERN == "right" then
                key = "right_shot"
            else
                key = (math.floor(frame / SHOT_INTERVAL) % 2) == 0
                    and "left_shot" or "right_shot"
            end
            log(string.format("progress: frame %d press %s pattern=%s",
                frame, key, SHOT_PATTERN))
            press(key, frame + SHOT_HOLD_FRAMES)
        end
    end

    if SNAPSHOT_FRAME > 0 and frame == SNAPSHOT_FRAME then
        ram_snapshot()
    end

    -- Poll the tilemap once per second: checksum change detection plus any
    -- ASCII text overlay.
    if frame % 30 == 0 then
        geometry_state()
        upload_state()
        local ok, sum = pcall(tile_checksum)
        if ok then
            if sum ~= last_screen_hash then
                last_screen_hash = sum
                local text_ok, text = pcall(screen_text)
                if text_ok and text:match("%S") then
                    log(string.format(
                        "progress: frame %d checksum %08x TEXT >>>\n%s\n<<< END",
                        frame, sum, text))
                else
                    log(string.format("progress: frame %d checksum %08x (graphics)",
                        frame, sum))
                end
            end
            -- Snapshot every second so menu flow can be reviewed visually.
            pcall(function() manager.machine.video:snapshot() end)
        else
            log("progress: checksum read failed at frame " .. frame)
        end
    end

    if frame >= TARGET_FRAMES then
        log("progress: session complete at frame " .. frame)
        manager.machine:exit()
    end
end)
