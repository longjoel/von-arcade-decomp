-- SCSP register write trace + sound-RAM snapshot for the offline renderer.
--
-- Produces the `W <time> <byte_offset_hex> <data_hex> <mem_mask_hex>` lines
-- consumed by `von-godot/native/scsp/von-scsp-render --trace`, plus a 512 KiB
-- sound-RAM binary for `--ram`. The sound-RAM write tap crashes this MAME
-- build (shared RAM region), so the RAM is snapshotted once at the end of the
-- capture instead, which is valid for steady-state music (select/title) whose
-- samples are uploaded before playback.
--
-- Environment: VON_SCSP_TRACE, VON_SCSP_RAM_DUMP, VON_SCSP_SECONDS,
--              VON_SCSP_RAM_FRAME (default = last frame),
--              VON_SCSP_BASE_SCRIPT (optional input-driving Lua to load first)

local REG_LOG = os.getenv("VON_SCSP_TRACE") or "vonj-scsp-regs.log"
local RAM_DUMP = os.getenv("VON_SCSP_RAM_DUMP") or "vonj-soundram.bin"
local SECONDS = tonumber(os.getenv("VON_SCSP_SECONDS") or "45")
local RAM_FRAME = tonumber(os.getenv("VON_SCSP_RAM_FRAME") or "0")

local base = os.getenv("VON_SCSP_BASE_SCRIPT")
if base and base ~= "" then
    dofile(base)
end

local audio = assert(manager.machine.devices[":audiocpu"], "missing :audiocpu")
local space = assert(audio.spaces[":program"] or audio.spaces["program"])

local reg_file = assert(io.open(REG_LOG, "w"))
local writes = 0
local function i(v, d) return math.floor(tonumber(v) or d) end

space:install_write_tap(0x100000, 0x100FFF, "von_reg",
    function(offset, data, mask)
        reg_file:write(string.format("W %.6f %x %x %x\n", emu.time(),
            i(offset, 0) - 0x100000, i(data, 0) & 0xffff,
            i(mask, 0xffff) & 0xffff))
        writes = writes + 1
        if writes % 65536 == 0 then reg_file:flush() end
    end)

local function dump_ram()
    local f = assert(io.open(RAM_DUMP, "wb"))
    local chunk = {}
    for addr = 0, 0x7FFFF do
        chunk[#chunk + 1] = string.char(space:read_u8(addr) & 0xff)
        if #chunk == 4096 then
            f:write(table.concat(chunk)); chunk = {}
        end
    end
    if #chunk > 0 then f:write(table.concat(chunk)) end
    f:close()
    print(string.format("von_scsp: dumped 0x80000 bytes of sound RAM to %s", RAM_DUMP))
end

local frame = 0
local dumped = false
emu.register_periodic(function()
    frame = frame + 1
    if RAM_FRAME > 0 and not dumped and frame >= RAM_FRAME then
        dumped = true
        dump_ram()
    end
    if emu.time() >= SECONDS then
        if not dumped then dumped = true; dump_ram() end
        reg_file:close()
        manager.machine:exit()
    end
end)

emu.add_machine_stop_notifier(function()
    pcall(function() reg_file:close() end)
end)
