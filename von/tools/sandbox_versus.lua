-- Movement sandbox: single-cabinet 2P versus with an idle P2 dummy,
-- a veto-frozen round timer, and a scripted P1 input program.
--
-- Rationale: one MAME instance exposes NO P2 input fields (verified by
-- field inventory), so a 2P-versus P2 that never receives input is the
-- closest thing to a NOP opponent. The round timer (0x500554 window) is
-- frozen by write taps that return the pre-write value, so the bout
-- never times out mid-program.
--
-- Env:
--   VON_SANDBOX_LOG        session log (default /tmp/sandbox.log)
--   VON_SANDBOX_FREEZE     1 to veto timer writes after recon (default 1)
--   VON_SANDBOX_RECON      timer-write log lines before veto starts (default 8)
--
-- Log vocabulary:
--   sandbox: lifecycle / boot / program markers
--   timer:   vetoed writes (pc, offset, data, mask) + freeze summary
--   watch:   periodic work-RAM reads (timer bytes, position candidates,
--            dispatcher cell) for post-run analysis
--   input:   program phase edges

local LOG_PATH = os.getenv("VON_SANDBOX_LOG") or "/tmp/sandbox.log"
local FREEZE = (os.getenv("VON_SANDBOX_FREEZE") or "1") == "1"
local RECON = tonumber(os.getenv("VON_SANDBOX_RECON") or "8") or 8

local log_file = assert(io.open(LOG_PATH, "w"))
local function log(msg)
    log_file:write(msg .. "\n")
    log_file:flush()
end

local TIMER_BASE = 0x500554
local TIMER_LEN = 4
local WATCH_WORDS = { timer0 = 0x500554, pos_a = 0x503b5c, pos_b = 0x503b68,
                      dispatch = 0x504d94 }

local frame = 0
local space = nil
local cpu_dev = nil
local battle = false
local space_logged = false

local function field(port, name)
    local p = manager.machine.ioport.ports[port]
    return p and p.fields[name] or nil
end

local F = {}
local pressed_until = {}

local function press(name, duration)
    if F[name] then
        F[name]:set_value(1)
        pressed_until[name] = frame + duration
    end
end

local function release(name)
    if F[name] then F[name]:clear_value() end
    pressed_until[name] = nil
end

local function hold_only(names)
    for name, _ in pairs(F) do
        local keep = false
        for _, want in ipairs(names) do
            if name == want then keep = true break end
        end
        if not keep then release(name) end
    end
    for _, want in ipairs(names) do press(want, 1000000) end
end

-- Timer veto tap: ONE tap over the aligned [TIMER_BASE, TIMER_BASE+3]
-- window (MAME rejects single-byte ranges: end needs low bits set).
-- Logs the first RECON writes (pc/mask reveal the true access width),
-- then returns the pre-write value to freeze the countdown. Per-byte
-- counts keyed by offset inside the callback.
local timer_tap = nil
local timer_seen = 0
local timer_vetoes = 0

local function install_timer_taps()
    if not space then return end
    local ok, tap = pcall(function()
        return space:install_write_tap(TIMER_BASE, TIMER_BASE + TIMER_LEN - 1,
            "sbxtimer",
            function(offset, data, mask)
                -- Reconstruct the pre-write word and veto byte-wise:
                -- keep bytes outside the write mask, restore vetoed bytes
                -- to their current (pre-write) values.
                local cur = data
                local okr, v = pcall(function()
                    if mask == 0xff then
                        return space:read_u8(offset)
                    else
                        return space:read_u32(offset & 0xfffffffc)
                    end
                end)
                if timer_seen < RECON then
                    local pc = "?"
                    if cpu_dev then
                        local okc, st = pcall(function()
                            return cpu_dev.state["CURPC"].value
                        end)
                        if okc and type(st) == "number" then
                            pc = string.format("0x%x", st)
                        end
                    end
                    log(string.format(
                        "timer: write @%08x pc=%s data=0x%x mask=0x%x cur=0x%x",
                        offset, pc, data, mask,
                        (okr and type(v) == "number") and v or 0))
                    timer_seen = timer_seen + 1
                elseif FREEZE then
                    timer_vetoes = timer_vetoes + 1
                    if okr and type(v) == "number" then cur = v end
                end
                return cur
            end)
    end)
    if ok and tap then
        timer_tap = tap
        log(string.format("sandbox: timer tap installed @%08x (freeze=%s)",
            TIMER_BASE, tostring(FREEZE)))
    else
        log("sandbox: WARNING timer tap failed")
    end
end

local function read_u32(addr)
    if not space then return nil end
    local ok, v = pcall(function() return space:read_u32(addr) end)
    if ok and type(v) == "number" then return v end
    return nil
end

local function watch(tag)
    local cells = {}
    for name, addr in pairs(WATCH_WORDS) do
        local v = read_u32(addr)
        cells[#cells + 1] = string.format("%s=%s", name,
            v and string.format("0x%08x", v) or "?")
    end
    log(string.format("watch: f%d %s %s", frame, tag, table.concat(cells, " ")))
end

emu.register_periodic(function()
    frame = frame + 1
    for name, until_frame in pairs(pressed_until) do
        if frame >= until_frame then release(name) end
    end

    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            cpu_dev = cpu
            space = cpu.spaces[":program"] or cpu.spaces["program"]
        end
        if space and not space_logged then
            space_logged = true
            local probe = read_u32(TIMER_BASE)
            log(string.format("sandbox: space acquired f%d probe=%s", frame,
                probe == nil and "nil" or string.format("0x%x", probe)))
        end
        if frame == 500 then
            local tags = {}
            for tag, _ in pairs(manager.machine.devices) do
                tags[#tags + 1] = tag
            end
            log("sandbox: device tags: " .. table.concat(tags, ","))
            if cpu_dev then
                local names = {}
                for name, _ in pairs(cpu_dev.spaces) do
                    names[#names + 1] = name
                end
                log("sandbox: maincpu spaces: " .. table.concat(names, ","))
            else
                log("sandbox: WARNING :maincpu device missing")
            end
        end
        if frame == 1 then
            F.coin = field(":IN0", "Coin 1")
            F.start2 = field(":IN0", "2 Players Start")
            F.left = field(":IN1", "P1 Left Stick/Left")
            F.right = field(":IN1", "P1 Left Stick/Right")
            F.up = field(":IN1", "P1 Left Stick/Up")
            F.dash = field(":IN1", "P1 Left Dash")
            local missing = {}
            for _, n in ipairs({"coin", "start2"}) do
                if not F[n] then missing[#missing + 1] = n end
            end
            if #missing > 0 then
                log("sandbox: FATAL missing boot fields: " .. table.concat(missing, ","))
                manager.machine:exit()
                return
            end
            for _, n in ipairs({"left", "right", "up", "dash"}) do
                if not F[n] then
                    log("sandbox: WARNING missing P1 field: " .. n)
                end
            end
            log("sandbox: fields resolved; P2 has no input fields on this cabinet (idle dummy by construction)")
        end
        return
    end

    -- Boot: coin, coin, 2P start (versus_mirror_probe timings).
    if frame == 7200 then press("coin", 8) end
    if frame == 7260 then press("coin", 8) end
    if frame == 7400 then press("start2", 10) end

    if frame == 9500 and not battle then
        battle = true
        install_timer_taps()
        watch("battle-start")
        log("sandbox: battle phase; program starts f9600")
    end

    if battle then
        if frame == 9600 then
            hold_only({"left"})
            log("input: phase strafe-left f9600-9840")
            watch("phase-edge")
        elseif frame == 9840 then
            hold_only({"right", "dash"})
            log("input: phase dash-right f9840-9960")
            watch("phase-edge")
        elseif frame == 9960 then
            hold_only({"up"})
            log("input: phase forward f9960-10080")
            watch("phase-edge")
        elseif frame == 10080 then
            hold_only({})
            log("input: phase idle f10080+")
            watch("phase-edge")
        end
        if frame % 120 == 0 then watch("periodic") end
    end

    if frame >= 10300 then
        watch("session-end")
        log(string.format("sandbox: complete (timer vetoes=%d)", timer_vetoes))
        hold_only({})
        manager.machine:exit()
    end
end)
