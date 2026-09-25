-- Minimal isolation probe: sound-RAM tap only, robust integer coercion.
local LOG = os.getenv("VON_SCSP_RAM_TRACE") or "/tmp/min-ram.log"
local audio = assert(manager.machine.devices[":audiocpu"])
local space = assert(audio.spaces[":program"] or audio.spaces["program"])
local f = assert(io.open(LOG, "w"))
local n = 0
local cur_frame = 0
local function i(v, d) return math.floor(tonumber(v) or d) end
space:install_write_tap(0x000000, 0x07FFFF, "vminram", function(offset, data, mask)
    f:write(string.format("R %d %x %x %x\n", cur_frame,
        i(offset, 0), i(data, 0) & 0xffff, i(mask, 0xffff) & 0xffff))
    n = n + 1
    if n % 4096 == 0 then f:flush() end
end)
local frame = 0
emu.register_periodic(function()
    frame = frame + 1
    cur_frame = frame
    if frame >= 480 then
        f:write(string.format("# writes=%d\n", n)); f:close(); manager.machine:exit()
    end
end)
