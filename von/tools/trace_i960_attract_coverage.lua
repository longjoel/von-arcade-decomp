-- Record every i960 ROM PC visited during an input-free attract-mode run.
-- Requires the Lua device_debug PC coverage extension in patch 0011.

local seconds = tonumber(os.getenv("VON_ATTRACT_SECONDS") or "60")
local output_path = os.getenv("VON_ATTRACT_PC_LOG") or "vonj-attract-pcs.txt"
local frame = 0
local cpu
local debug
local started = false
local written = false

local function start_tracking()
    cpu = manager.machine.devices[":maincpu"]
    debug = cpu and cpu.debug or nil
    if not debug then
        return false
    end
    debug:track_pc(true, true)
    started = true
    return true
end

local function write_coverage()
    if written or not started then
        return
    end
    written = true
    local output = assert(io.open(output_path, "w"))
    local count = 0
    output:write(string.format("# set=vonj seconds=%d frames=%d\n", seconds, frame))
    for address = 0, 0x001ffffc, 4 do
        if debug:track_pc_visited(address) then
            output:write(string.format("%08x\n", address))
            count = count + 1
        end
    end
    output:write(string.format("# visited=%d\n", count))
    output:close()
    debug:track_pc(false, false)
end

-- Use emulated time rather than callback count: periodic callbacks are a
-- UI/debug timer, and frame-done callbacks are not delivered with -video none.
emu.register_periodic(function()
	frame = frame + 1
	if not started then
		start_tracking()
	end
	if started and emu.time() >= seconds then
		emu.exit()
	end
end)

-- Retain the subscription after the autoboot chunk returns.  Notifier
-- subscriptions unregister when garbage-collected.
_G.von_pc_stop_subscription = emu.add_machine_stop_notifier(write_coverage)
