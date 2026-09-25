-- Runtime probe: i960 sound-command queue plus 68000 SCSP slot writes.
--
-- Read-only.  Records, per emulated frame, the raw write address/data and
-- CURPC for:
--   q  i960 0x51aa70-0x51aabf   host sound-command ring (indices + 64 bytes)
--   s  68k  0x100000-0x100fff   SCSP register/slot writes
--   b  68k  0x400000-0x400001   sample-bank control
--
-- The output is grouped offline: queue byte stores reconstruct the `ae HH LL`
-- commands, and the SCSP writes reconstruct each slot's sample address and
-- envelope so a command can be tied to the played sample.
--
-- Environment: VON_VOICE_LOG      (default vonj-scsp-voices.log)
--              VON_VOICE_SECONDS  (default 30)
--              VON_VOICE_MAX      (max records, default 400000)

local LOG = os.getenv("VON_VOICE_LOG") or "vonj-scsp-voices.log"
local SECONDS = tonumber(os.getenv("VON_VOICE_SECONDS") or "30")
local MAX = tonumber(os.getenv("VON_VOICE_MAX") or "400000")

local file = assert(io.open(LOG, "w"))
local frame = 0
local records = 0

local function log(line)
    if records >= MAX then return end
    file:write(line .. "\n")
    records = records + 1
end

local main_cpu = manager.machine.devices[":maincpu"]
local audio_cpu = manager.machine.devices[":audiocpu"]
if not audio_cpu then
    for _, dev in pairs(manager.machine.devices) do
        local ok, short = pcall(function() return dev.shortname end)
        if ok and short == "m68000" then audio_cpu = dev end
    end
end
assert(main_cpu and audio_cpu, "missing maincpu/audiocpu")

local main_space = main_cpu.spaces[":program"] or main_cpu.spaces["program"]
local audio_space = audio_cpu.spaces[":program"] or audio_cpu.spaces["program"]
assert(main_space and audio_space, "missing program spaces")

local function pc_of(cpu)
    local ok, entry = pcall(function()
        return cpu.state["CURPC"] or cpu.state["GENPC"]
    end)
    if ok and entry then
        return tonumber(entry.value) or 0
    end
    return 0
end

local function install(space, cpu, first, last, tag)
    local ok, tap = pcall(function()
        return space:install_write_tap(first, last, "von_" .. tag,
            function(addr, data)
                log(string.format("f %d %s w %08x %08x %08x",
                    frame, tag, addr & 0xffffffff, data & 0xffffffff,
                    pc_of(cpu)))
            end)
    end)
    if not ok then
        file:write(string.format("# tap %s failed: %s\n", tag, tostring(tap)))
    end
end

install(main_space, main_cpu, 0x0051AA70, 0x0051AABF, "q")
install(audio_space, audio_cpu, 0x00100000, 0x00100FFF, "s")
install(audio_space, audio_cpu, 0x00400000, 0x00400001, "b")

file:write(string.format("# scsp-voice-probe seconds=%.3f\n", SECONDS))
file:flush()

emu.register_periodic(function()
    frame = frame + 1
    if emu.time() >= SECONDS or records >= MAX then
        file:close()
        manager.machine:exit()
    end
end)

emu.add_machine_stop_notifier(function()
    pcall(function() file:close() end)
end)
