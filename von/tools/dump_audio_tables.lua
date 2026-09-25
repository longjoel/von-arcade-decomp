-- One-shot read-only dump of the 68000 sound driver's initialized tables.
--
-- Attract mode initializes the driver but never faults, so at a chosen frame
-- this prints the channel records (0x4000), the relocated sequence table
-- (0x9000), the descriptor-table copy (0x5000), and the voice records
-- (0x2800) as raw hex for offline decoding. No writes, no input.
--
-- Environment: VON_TABLES_LOG (default vonj-audio-tables.log)
--              VON_TABLES_FRAME (default 600)

local LOG = os.getenv("VON_TABLES_LOG") or "vonj-audio-tables.log"
local AT = tonumber(os.getenv("VON_TABLES_FRAME") or "600")

local cpu = assert(manager.machine.devices[":audiocpu"], "missing :audiocpu")
local space = assert(cpu.spaces[":program"] or cpu.spaces["program"])
local file = assert(io.open(LOG, "w"))
local frame = 0
local done = false

local function dump(name, base, length)
    local bytes = {}
    for offset = 0, length - 1 do
        bytes[#bytes + 1] = string.format("%02x", space:read_u8(base + offset))
    end
    file:write(string.format("%s %08x %04x %s\n", name, base, length,
        table.concat(bytes)))
end

emu.register_periodic(function()
    frame = frame + 1
    if not done and frame >= AT then
        done = true
        dump("channels", 0x00004000, 0x0140)   -- 20 * 16
        dump("relocated", 0x00009000, 0x0600)  -- sequence table
        dump("descriptors", 0x00005000, 0x0380) -- 56 * 16
        dump("voices", 0x00002800, 0x0200)     -- 32 * 16
        file:close()
        manager.machine:exit()
    end
end)
