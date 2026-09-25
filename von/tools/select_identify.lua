-- Identify the machine-select cursor values by snapshotting each dwell.
-- Coins in, steps the cursor one value at a time (single-frame press), dwells,
-- and writes cursor-<hex>.png per distinct non-zero cursor byte.
--
-- Env: VON_ID_DIR (/tmp/von-id), VON_ID_COIN (900), VON_ID_DWELL (120),
--      VON_ID_MAX (14), VON_ID_CURSOR (0x500550)

local DIR = os.getenv("VON_ID_DIR") or "/tmp/von-id"
local COIN = tonumber(os.getenv("VON_ID_COIN") or "900")
local DWELL = tonumber(os.getenv("VON_ID_DWELL") or "120")
local MAX = tonumber(os.getenv("VON_ID_MAX") or "14")
local CURSOR = tonumber(os.getenv("VON_ID_CURSOR") or "0x500550")
os.execute("mkdir -p '" .. DIR .. "'")

local frame = 0
local cpu, space, coin, start, right

local function setup()
	cpu = manager.machine.devices[":maincpu"]
	if not cpu then return false end
	space = cpu.spaces[":program"] or cpu.spaces["program"]
	if not space then return false end
	local in0 = manager.machine.ioport.ports[":IN0"]
	local in1 = manager.machine.ioport.ports[":IN1"]
	if not (in0 and in1) then return false end
	coin = in0.fields["Coin 1"]
	start = in0.fields["1 Player Start"]
	right = in1.fields["P1 Left Stick/Right"]
	return right ~= nil
end

local last, dwell, steps, hold = nil, 0, 0, 0
local snapped = {}

emu.register_periodic(function()
	frame = frame + 1
	if not coin then
		if not setup() then return end
	end
	if coin then
		if frame >= COIN and frame < COIN + 10 then coin:set_value(1) else coin:clear_value() end
	end
	if start then start:clear_value() end
	if right then right:clear_value() end

	if frame < COIN + 90 then
		return
	end
	local c = space:read_u8(CURSOR)
	if last == nil then
		last = c
		dwell = DWELL
		return
	end
	if c ~= last then
		last = c
		if c ~= 0 then
			dwell = DWELL
			steps = steps + 1
		end
		return
	end
	if dwell > 0 then
		if c ~= 0 and dwell == DWELL - 30 and not snapped[c] then
			snapped[c] = true
			local s = manager.machine.screens[":screen"]
			if s then
				pcall(function() s:snapshot(string.format("%s/cursor-%02x.png", DIR, c)) end)
				emu.print_info(string.format("IDENT cursor=%02x frame=%d", c, frame))
			end
		end
		dwell = dwell - 1
		return
	end
	if hold > 0 then
		hold = hold - 1
		if right then right:set_value(1) end
		return
	end
	if steps < MAX then
		hold = 1
	end
end)
