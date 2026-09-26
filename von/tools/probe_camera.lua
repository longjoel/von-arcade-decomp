-- Camera recovery probe: join the first bout, force a known stage, and drive a
-- turn/move pattern so the third-person camera sweeps. Pair with -oslog; the
-- view matrix is the matrix reused across the family-0x80 world statics in
-- each frame (see von/i960/rom-hacking.md).
--
-- Env:
--   VON_CAMERA_LOG        required Lua log path (frame + banner + ordinal)
--   VON_CAMERA_ORDINAL    stage ordinal to force (default 1 = AIRPORT)
--   VON_CAMERA_SECONDS    run length in emulated seconds (default 70)
--   VON_CAMERA_FROM       first driven frame (default 1800)
--   VON_CAMERA_STEP       frames per pattern phase (default 90)
--   VON_CAMERA_STATE      "base,len[,every]" hex words logged every frame
--   VON_CAMERA_HOLD       "PORT,mask,from,to" hold one input instead of the
--                         turn/move pattern (e.g. ":IN1,0x20,2100,4200")

local LOG = assert(os.getenv("VON_CAMERA_LOG"), "VON_CAMERA_LOG required")
local ORD = tonumber(os.getenv("VON_CAMERA_ORDINAL") or "1")
local SECONDS = tonumber(os.getenv("VON_CAMERA_SECONDS") or "70")
local FROM = tonumber(os.getenv("VON_CAMERA_FROM") or "1800")
local STEP = tonumber(os.getenv("VON_CAMERA_STEP") or "90")
local HOLD = os.getenv("VON_CAMERA_HOLD")
local SEQUENCE = {}
do
	local raw = os.getenv("VON_CAMERA_SEQ") or ""
	for tok in string.gmatch(raw, "([^;]+)") do
		local port, mask, from, to = string.match(tok, "([^,]+),([^,]+),([^,]+),([^,]+)")
		if port then
			SEQUENCE[#SEQUENCE + 1] = {
				port = ":" .. port:gsub("^:", ""), mask = tonumber(mask),
				from = tonumber(from), to = tonumber(to),
			}
		end
	end
end
local hold
-- Field-name schedule (preferred over masks for motion probes):
--   VON_CAMERA_FIELD_SEQ="from,to,PORT:FIELD[,PORT:FIELD];from,to,..."
-- Each window presses the named ioport fields (e.g. jump = left stick left +
-- right stick right, melee = both shots). One run can sweep idle/dash/jump/...
local FIELD_SEQ = {}
do
	local raw = os.getenv("VON_CAMERA_FIELD_SEQ") or ""
	for tok in string.gmatch(raw, "([^;]+)") do
		local from, to, spec = string.match(tok, "([^,]+),([^,]+),(.+)")
		if from then
			local fields = {}
			for item in string.gmatch(spec, "([^,]+)") do
				local port, name = string.match(item, "([^:]+):(.+)")
				if port then
					fields[#fields + 1] = { port = ":" .. port:gsub("^:", ""), name = name }
				end
			end
			FIELD_SEQ[#FIELD_SEQ + 1] = { from = tonumber(from), to = tonumber(to), fields = fields }
		end
	end
end
local STATE = os.getenv("VON_CAMERA_STATE")
local state_base, state_len, state_every
if STATE then
	state_base, state_len, state_every = string.match(STATE, "([^,]+),([^,]+),?([^,]*)")
	state_base, state_len = tonumber(state_base), tonumber(state_len)
	state_every = tonumber(state_every) or 1
end
do
	local port, mask, from, to
	if HOLD then
		port, mask, from, to = string.match(HOLD, "([^,]+),([^,]+),([^,]+),([^,]+)")
	end
	if port then
		hold = { port = port, mask = tonumber(mask), from = tonumber(from), to = tonumber(to) }
	end
end
local out = assert(io.open(LOG, "w"))

local frame = 0
local space = nil

local function field(port, name)
	local p = manager.machine.ioport.ports[port]
	return p and p.fields[name] or nil
end

local function setp(name, port, pressed)
	local f = field(port, name)
	if not f then return end
	local mask = f.mask or 1
	local def = f.defvalue or mask
	local inactive = def & mask
	local active = (inactive == 0) and mask or 0
	f:set_value(pressed and active or inactive)
end

-- Press the field in `port` whose bitmask is `mask`. Avoids depending on the
-- auto-generated joystick field names.
local function setmask(port, mask, pressed)
	local p = manager.machine.ioport.ports[port]
	if not p then return end
	for _, f in pairs(p.fields) do
		if (f.mask or 0) == mask then
			local def = f.defvalue or mask
			local inactive = def & mask
			local active = (inactive == 0) and mask or 0
			f:set_value(pressed and active or inactive)
		end
	end
end

local function r(a)
	if not space then return -1 end
	local ok, v = pcall(function() return space:read_u32(a) end)
	return ok and v or -1
end

-- Pattern phases: 0 turn left, 1 turn right, 2 forward, 3 reverse.
local PHASES = {
	{ port = ":IN2", mask = 0x80, name = "turn-left" },
	{ port = ":IN2", mask = 0x40, name = "turn-right" },
	{ port = ":IN1", mask = 0x20, name = "forward" },
	{ port = ":IN1", mask = 0x10, name = "reverse" },
}

local phase = -1
emu.register_periodic(function()
	frame = frame + 1
	if not space then
		local cpu = manager.machine.devices[":maincpu"]
		if cpu then space = cpu.spaces[":program"] or cpu.spaces["program"] end
	end
	setp("Coin 1", ":IN0", frame >= 900 and frame < 905)
	setp("1 Player Start", ":IN0", frame >= 1500 and frame < 1508)
	if space and frame >= 1600 and frame <= 4200 then
		pcall(function()
			space:write_u32(0x503a80, ORD)
			space:write_u32(0x509b80, ORD)
		end)
	end
	if hold then
		setmask(hold.port, hold.mask, frame >= hold.from and frame < hold.to)
	end
	for _, s in ipairs(SEQUENCE) do
		setmask(s.port, s.mask, frame >= s.from and frame < s.to)
	end
	for _, w in ipairs(FIELD_SEQ) do
		local active = frame >= w.from and frame < w.to
		for _, f in ipairs(w.fields) do
			setp(f.name, f.port, active)
		end
	end
	local next_phase = -1
	if not hold and #SEQUENCE == 0 and #FIELD_SEQ == 0 and frame >= FROM then
		next_phase = math.floor((frame - FROM) / STEP) % #PHASES
	end
	if not hold and #SEQUENCE == 0 and next_phase ~= phase then
		phase = next_phase
		for _, p in ipairs(PHASES) do
			setmask(p.port, p.mask, false)
		end
		if phase >= 0 then
			local p = PHASES[phase + 1]
			setmask(p.port, p.mask, true)
			out:write(string.format("f%d phase=%s\n", frame, p.name))
			out:flush()
		end
	end
	if space and frame % 30 == 0 then
		out:write(string.format("f%d ord=%d banner=%08x\n", frame, r(0x503a80), r(0x5770f0)))
		out:flush()
	end
	if state_base and space and frame % state_every == 0 then
		local words = {}
		for a = state_base, state_base + state_len - 1, 4 do
			words[#words + 1] = string.format("%08x", r(a))
		end
		out:write(string.format("f%d state %s\n", frame, table.concat(words, " ")))
	end
	if frame >= SECONDS * 60 then
		out:close()
		manager.machine:exit()
	end
end)
