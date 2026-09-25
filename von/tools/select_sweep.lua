-- Controlled machine-select sweep: press Right, wait for the cursor byte to
-- change, then dwell so each fighter's 3D preview is captured. Works around
-- key-repeat skipping fighters.
--
-- Env: VON_SWEEP_COIN (900), VON_SWEEP_DWELL (150), VON_SWEEP_HOLD (14),
--      VON_SWEEP_MAX (12), VON_SWEEP_CURSOR (0x500550)

local COIN_FRAME = tonumber(os.getenv("VON_SWEEP_COIN") or "900")
local DWELL = tonumber(os.getenv("VON_SWEEP_DWELL") or "150")
local HOLD = tonumber(os.getenv("VON_SWEEP_HOLD") or "3")
local MAX_STEPS = tonumber(os.getenv("VON_SWEEP_MAX") or "12")
local CURSOR = tonumber(os.getenv("VON_SWEEP_CURSOR") or "0x500550")

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

local function log(msg)
	emu.print_info("sweep: " .. msg)
end

local last = nil
local dwell = 0
local steps = 0
local hold = 0
local seen = {}

emu.register_periodic(function()
	frame = frame + 1
	if not coin then
		if not setup() then return end
	end

	if coin then
		if frame >= COIN_FRAME and frame < COIN_FRAME + 10 then coin:set_value(1) else coin:clear_value() end
	end
	if start then start:clear_value() end
	if right then right:clear_value() end

	if frame < COIN_FRAME + 90 then
		return
	end

	local c = space:read_u8(CURSOR)

	if last == nil then
		last = c
		dwell = DWELL
		log(string.format("cursor start=%02x frame=%d", c, frame))
		return
	end

	if c ~= last then
		last = c
		if c ~= 0 then
			dwell = DWELL
			steps = steps + 1
			seen[c] = true
			log(string.format("cursor=%02x step=%d frame=%d", c, steps, frame))
		end
		return
	end

	if dwell > 0 then
		dwell = dwell - 1
		return
	end

	if hold > 0 then
		hold = hold - 1
		if right then right:set_value(1) end
		return
	end

	if steps < MAX_STEPS then
		hold = HOLD
	end
end)
