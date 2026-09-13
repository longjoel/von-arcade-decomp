-- Virtual-On hacking driver: join a bout, force cells, log write watchpoints,
-- mirror the geometry matrix, draw an overlay, and capture PNG+state sidecars.
--
-- This is a probe harness, not evidence tooling. It pushes values into work RAM
-- and sets debugger watchpoints to find writers, then dumps a sidecar next to
-- each screenshot for camera/state analysis.
--
-- Env:
--   VON_HACK_LOG          log path (default /tmp/von-hack.log)
--   VON_HACK_SECONDS      run length (default 60)
--   VON_HACK_COIN_FRAME   Coin 1 pulse frame (default 900)
--   VON_HACK_START_FRAME  1P Start pulse frame (default 1500)
--   VON_FORCE             "addr=val;..." written every frame after VON_FORCE_FROM
--   VON_FORCE_FROM        first force frame (default 0)
--   VON_WP                "addr,len[,type];..." write/read watchpoints (type r/w/rw, default w)
--   VON_MIRROR            dump the matrix slot (0x5ff000, 12 words) every N frames (0 off, default 30)
--   VON_HACK_SNAP_EVERY   snapshot + sidecar every N frames (0 off, default 0)
--   VON_HACK_SNAP_FRAME   single snapshot frame
--   VON_HACK_SNAP_DIR     snapshot directory (PNG + sidecar)
--   VON_OVERLAY           "addr:label;..." drawn top-left

local LOG = os.getenv("VON_HACK_LOG") or "/tmp/von-hack.log"
local SECONDS = tonumber(os.getenv("VON_HACK_SECONDS") or "60")
local COIN = tonumber(os.getenv("VON_HACK_COIN_FRAME") or "900")
local START = tonumber(os.getenv("VON_HACK_START_FRAME") or "1500")
local FORCE_FROM = tonumber(os.getenv("VON_FORCE_FROM") or "0")
local MIRROR = tonumber(os.getenv("VON_MIRROR") or "30")
local SNAP_EVERY = tonumber(os.getenv("VON_HACK_SNAP_EVERY") or "0")
local SNAP_FRAME = tonumber(os.getenv("VON_HACK_SNAP_FRAME") or "0")
local SNAP_DIR = os.getenv("VON_HACK_SNAP_DIR")
local MATRIX_BASE = 0x5ff000

local out = assert(io.open(LOG, "w"))
local function log(m) out:write(m .. "\n"); out:flush() end

local frame = 0
local space, cpu, debug
local forced, watchpoints, overlay = {}, {}, {}
do
	local raw = os.getenv("VON_FORCE")
	if raw then
		for tok in string.gmatch(raw, "([^;]+)") do
			local a, v = string.match(tok, "([^=]+)=(.*)")
			if a then forced[#forced + 1] = { addr = tonumber(a), val = tonumber(v), } end
		end
	end
end
do
	local raw = os.getenv("VON_WP")
	if raw then
		for tok in string.gmatch(raw, "([^;]+)") do
			local a, l, t = string.match(tok, "([^,]+),([^,]+),?(%a*)")
			if a then
				watchpoints[#watchpoints + 1] = { addr = tonumber(a), len = tonumber(l) or 4, type = (t ~= "" and t) or "w" }
			end
		end
	end
end
do
	local raw = os.getenv("VON_OVERLAY")
	if raw then
		for tok in string.gmatch(raw, "([^;]+)") do
			local a, name = string.match(tok, "([^:]+):(.*)")
			if a then overlay[#overlay + 1] = { addr = tonumber(a), name = name } end
		end
	end
end

local function rd32(a)
	if not space then return 0 end
	local ok, v = pcall(function() return space:read_u32(a) end)
	return ok and v or 0
end
local function field(port, name)
	local p = manager.machine.ioport.ports[port]
	return p and p.fields[name] or nil
end
local function setp(name, port, pressed)
	local f = field(port, name); if not f then return end
	local mask = f.mask or 1
	local def = f.defvalue or mask
	local inactive = def & mask
	local active = (inactive == 0) and mask or 0
	f:set_value(pressed and active or inactive)
end

local REGS = { "CURPC", "pc", "ip", "pip", "pfp", "sp", "fp", "rip", "sat",
	"r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15",
	"g0", "g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", "g9", "g10", "g11", "g12", "g13", "g14" }

local function json_escape(s) return (tostring(s):gsub('"', '\\"')) end

local function sidecar(name)
	if not SNAP_DIR then return end
	os.execute("mkdir -p " .. SNAP_DIR)
	if manager.machine.video then pcall(function() manager.machine.video:snapshot() end) end
	local f = io.open(string.format("%s/%s.json", SNAP_DIR, name), "w")
	f:write("{\n")
	f:write(string.format('  "name": "%s",\n', json_escape(name)))
	f:write(string.format('  "frame": %d,\n', frame))
	f:write('  "registers": {')
	local first = true
	for _, r in ipairs(REGS) do
		local ok, v = pcall(function() return cpu.state[r].value end)
		if ok and type(v) == "number" then
			f:write(string.format('%s"%s": %d', first and "" or ", ", r, v))
			first = false
		end
	end
	f:write("},\n")
	f:write('  "matrix_slot": [')
	for i = 0, 11 do f:write(string.format("%s%d", i == 0 and "" or ", ", rd32(MATRIX_BASE + i * 4))) end
	f:write("],\n")
	f:write('  "workram": {')
	for i, o in ipairs(overlay) do
		f:write(string.format('%s"%s": %d', i == 1 and "" or ", ", json_escape(o.name), rd32(o.addr)))
	end
	f:write("}\n}\n")
	f:close()
	log(string.format("snap %s f%d", name, frame))
end

local installed = false
emu.register_periodic(function()
	frame = frame + 1
	if not space then
		cpu = manager.machine.devices[":maincpu"]
		if cpu then
			space = cpu.spaces[":program"] or cpu.spaces["program"]
			debug = cpu.debug
		end
	end
	-- join
	setp("Coin 1", ":IN0", frame >= COIN and frame < COIN + 5)
	setp("1 Player Start", ":IN0", frame >= START and frame < START + 8)
	-- force cells each frame
	if space and frame >= FORCE_FROM then
		for _, fspec in ipairs(forced) do
			pcall(function() space:write_u32(fspec.addr, fspec.val) end)
		end
	end
	-- install watchpoints once the debugger is up
	if debug and not installed and frame > 1 then
		installed = true
		for _, w in ipairs(watchpoints) do
			local ok, id = pcall(function() return debug:wpset(space, w.type, w.addr, w.len, "", "go") end)
			log(string.format("wp %08x len %d type %s -> %s", w.addr, w.len, w.type, tostring(ok and id or "fail")))
		end
	end
	if space and MIRROR > 0 and frame % MIRROR == 0 then
		local m = {}
		for i = 0, 11 do m[#m + 1] = string.format("%08x", rd32(MATRIX_BASE + i * 4)) end
		log(string.format("matrix f%d %s", frame, table.concat(m, " ")))
	end
	if SNAP_DIR and SNAP_EVERY > 0 and frame % SNAP_EVERY == 0 then
		sidecar(string.format("f%06d", frame))
	end
	if SNAP_DIR and SNAP_FRAME > 0 and frame == SNAP_FRAME then
		sidecar(string.format("f%06d", frame))
	end
	-- overlay
	if #overlay > 0 then
		pcall(function()
			local ui = manager.machine.render.ui_container
			if ui then
				for i, o in ipairs(overlay) do
					ui:draw_text(0.01, 0.01 + (i - 1) * 0.03,
						string.format("%s=%08x", o.name, rd32(o.addr)), 0xff00ff00)
				end
			end
		end)
	end
	if frame >= SECONDS * 60 then out:close(); manager.machine:exit() end
end)
