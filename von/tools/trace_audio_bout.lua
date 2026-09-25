-- Arena-selector + sound-command tap composed with the sandbox input program.
local LOG = os.getenv("VON_BOUT_QUEUE_LOG") or "/tmp/von-bout-queue.log"
local base = os.getenv("VON_SANDBOX_BASE") or "/src/von/tools/sandbox_versus.lua"
local main = assert(manager.machine.devices[":maincpu"])
local space = assert(main.spaces[":program"] or main.spaces["program"])
local f = assert(io.open(LOG, "w"))
local function tap(first, last, tag)
    local ok = pcall(function()
        space:install_write_tap(first, last, "von_" .. tag, function(offset, data)
            f:write(string.format("%s %.6f %x %x\n", tag, emu.time(), offset, data & 0xff))
            f:flush()
        end)
    end)
    f:write(string.format("# tap %s ok=%s\n", tag, tostring(ok))); f:flush()
end
tap(0x0051AA70, 0x0051AABF, "Q")   -- sound-command ring
tap(0x005770F0, 0x005770F3, "S")   -- arena selector
dofile(base)
