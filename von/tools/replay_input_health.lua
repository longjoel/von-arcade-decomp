-- Passive replay probe: log live input-port changes plus fighter health.
--
-- Replays a recorded .inp (via MAME -playback) and records, per emulated
-- frame, any change in the raw :IN0/:IN1/:IN2 port values alongside the
-- player/CPU health halfwords and the session/round ticks. Used to
-- correlate button presses with damage events when reconstructing gameplay
-- routines. Never injects input; safe under -playback.
--
-- Environment: VON_IH_LOG     (log file path)
--              VON_IH_SECONDS  (default 260 emulated seconds)

local SECONDS = tonumber(os.getenv("VON_IH_SECONDS") or "260")
local TARGET_FRAMES = SECONDS * 60
local LOG_PATH = os.getenv("VON_IH_LOG") or "vonj-input-health.log"

local log_file = assert(io.open(LOG_PATH, "w"))

local function log(msg)
    log_file:write(msg .. "\n")
    log_file:flush()
end

local frame = 0
local space = nil
local ports = nil
local last_ports = nil
local last_php = nil
local last_chp = nil
local last_pb = nil
local last_cb = nil
local last_sa = nil
local last_sh = nil

-- Optional write tap: VON_IH_WTAP_ADDR (hex), VON_IH_WTAP_COUNT (default
-- 20000), VON_IH_WTAP_START (install at frame, default 0). Logs the
-- CURPC behind each write so the damage applier's store instructions can
-- be identified in the disassembly.
local wtap_addr = tonumber(os.getenv("VON_IH_WTAP_ADDR") or "0")
local wtap_end = tonumber(os.getenv("VON_IH_WTAP_END") or "0")
local wtap_count = tonumber(os.getenv("VON_IH_WTAP_COUNT") or "20000")
local wtap_start = tonumber(os.getenv("VON_IH_WTAP_START") or "0")
local wtap = nil
local wtap_hits = 0

-- Optional read tap: VON_IH_RTAP_ADDR/END/COUNT/START. Logs CURPC behind
-- each read to find consumers of fields like the beam budget (+0x1d6).
local rtap_addr = tonumber(os.getenv("VON_IH_RTAP_ADDR") or "0")
local rtap_end = tonumber(os.getenv("VON_IH_RTAP_END") or "0")
local rtap_count = tonumber(os.getenv("VON_IH_RTAP_COUNT") or "20000")
local rtap_start = tonumber(os.getenv("VON_IH_RTAP_START") or "0")
local rtap = nil
local rtap_hits = 0

local function rtap_poll()
    if rtap or rtap_addr <= 0 or frame < rtap_start then
        return
    end
    if rtap_end <= rtap_addr then
        rtap_end = rtap_addr + 3
    end
    local ok, tap = pcall(function()
        return space:install_read_tap(rtap_addr, rtap_end, "ihrtap",
            function(addr)
                rtap_hits = rtap_hits + 1
                local pc = "?"
                local pok, st = pcall(function()
                    return manager.machine.devices[":maincpu"].state["CURPC"].value
                end)
                if pok and type(st) == "number" then
                    pc = string.format("0x%x", st)
                end
                log(string.format("r f %d addr=0x%x pc=%s",
                    frame, addr, pc))
                if rtap_hits >= rtap_count and rtap then
                    space:uninstall_read_tap(rtap)
                    log("ih: read tap removed")
                end
            end)
    end)
    if ok and tap then
        rtap = tap
        log(string.format("ih: read tap installed at 0x%x-0x%x", rtap_addr, rtap_end))
    else
        log(string.format("ih: read tap FAILED at 0x%x-0x%x", rtap_addr, rtap_end))
        rtap_addr = 0
    end
end

local function wtap_poll()
    if wtap or wtap_addr <= 0 or frame < wtap_start then
        return
    end
    if wtap_end <= wtap_addr then
        wtap_end = wtap_addr + 3
    end
    local ok, tap = pcall(function()
        return space:install_write_tap(wtap_addr, wtap_end, "ihwtap",
            function(addr, data)
                wtap_hits = wtap_hits + 1
                local pc = "?"
                local pok, st = pcall(function()
                    return manager.machine.devices[":maincpu"].state["CURPC"].value
                end)
                if pok and type(st) == "number" then
                    pc = string.format("0x%x", st)
                end
                log(string.format("w f %d addr=0x%x data=0x%x pc=%s",
                    frame, addr, data, pc))
                if wtap_hits >= wtap_count and wtap then
                    space:uninstall_write_tap(wtap)
                    log("ih: write tap removed")
                end
            end)
    end)
    if ok and tap then
        wtap = tap
        log(string.format("ih: write tap installed at 0x%x-0x%x", wtap_addr, wtap_end))
    else
        log(string.format("ih: write tap FAILED at 0x%x-0x%x", wtap_addr, wtap_end))
        wtap_addr = 0
    end
end

local PHP_ADDR = 0x00503ca2
local CHP_ADDR = 0x0050380a
local FC_ADDR = 0x005039fc

local function setup()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then
        return false
    end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    if not space then
        return false
    end
    local in0 = manager.machine.ioport.ports[":IN0"]
    local in1 = manager.machine.ioport.ports[":IN1"]
    local in2 = manager.machine.ioport.ports[":IN2"]
    if not in0 or not in1 or not in2 then
        return false
    end
    ports = { in0, in1, in2 }
    log("ih: ports resolved")
    return true
end

local function read_u16(addr)
    local ok, v = pcall(function() return space:read_u16(addr) end)
    if ok and type(v) == "number" then
        return v
    end
    return nil
end

local function read_u32(addr)
    local ok, v = pcall(function() return space:read_u32(addr) end)
    if ok and type(v) == "number" then
        return v
    end
    return nil
end

emu.register_periodic(function()
    frame = frame + 1
    if not space and frame % 60 == 1 then
        if not setup() then
            return
        end
    end
    if not space then
        return
    end

    wtap_poll()
    rtap_poll()

    -- Optional uniform position sampling: VON_IH_POS=1 logs both shadows'
    -- float xyz (+0x8/+0xc/+0x10) every frame for velocity profiling.
    if os.getenv("VON_IH_POS") == "1" then
        local px = read_u32(0x00503ad8)
        local py = read_u32(0x00503adc)
        local pz = read_u32(0x00503ae0)
        local cx = read_u32(0x005040d8)
        local cy = read_u32(0x005040dc)
        local cz = read_u32(0x005040e0)
        log(string.format("p f %d px %s py %s pz %s cx %s cy %s cz %s",
            frame, tostring(px), tostring(py), tostring(pz),
            tostring(cx), tostring(cy), tostring(cz)))
    end

    local p0, p1, p2 = nil, nil, nil
    local ok = pcall(function()
        p0 = ports[1]:read()
        p1 = ports[2]:read()
        p2 = ports[3]:read()
    end)
    if not ok then
        return
    end

    local php = read_u16(PHP_ADDR)
    local chp = read_u16(CHP_ADDR)
    local php = read_u16(PHP_ADDR)
    local chp = read_u16(CHP_ADDR)
    local pb = read_u16(0x00503ca4)
    local cb = read_u16(0x005042a4)
    local sa = read_u16(0x005042a0)
    local sh = read_u16(0x005042a2)

    local ports_key = string.format("%x/%x/%x", p0, p1, p2)
    if ports_key ~= last_ports or php ~= last_php or chp ~= last_chp
            or pb ~= last_pb or cb ~= last_cb
            or sa ~= last_sa or sh ~= last_sh then
        local fc = read_u32(FC_ADDR)
        log(string.format("f %d in0 %x in1 %x in2 %x php %s chp %s pb %s cb %s sa %s sh %s fc %s",
            frame, p0, p1, p2, tostring(php), tostring(chp),
            tostring(pb), tostring(cb), tostring(sa), tostring(sh),
            tostring(fc)))
        last_ports = ports_key
        last_php = php
        last_chp = chp
        last_pb = pb
        last_cb = cb
        last_sa = sa
        last_sh = sh
    end

    if frame >= TARGET_FRAMES then
        log("ih: session complete at frame " .. frame)
        manager.machine:exit()
    end
end)
