-- Stage -> arena/banner binding probe.
--
-- Joins the deterministic first match (Coin 1 @900, 1 Player Start @1500; the
-- first opponent and arena are fixed) and, inside a window, forces the
-- stage-ordinal cells 0x503a80 / 0x509b80 to VON_STAGE_ORDINAL. It logs the
-- stage descriptor the loader publishes (0x504ca0/cb0/cc0), the banner page
-- word 0x5770f0, and the selector timers, so the ordinal -> banner permutation
-- can be read directly:
--
--   0x5770f0 == word1 of the 32-byte record at 0x194a0[ord * 32]
--
-- Pair with the instrumented geometry trace (patch 0007) via -oslog to census
-- the OBA families each stage serves.
--
-- Recovered 2026-09-12: ordinal -> banner = [7,0,2,3,4,9,5,6,1,8] over the ROM
-- banner order (AIRPORT..SECRET BASE at 0x21065). Live-confirmed for all ten
-- ordinals. The same runs census each ordinal's arena OBA set and show the
-- recovered family-0x80 statics belong to ordinal 1 (AIRPORT), not ordinal 0;
-- see von/i960/stage-arena-binding.md.
--
-- Env:
--   VON_STAGE_LOG          required output path
--   VON_STAGE_ORDINAL      ordinal to force (default 0)
--   VON_STAGE_FORCE_MIRROR 1 to also force 0x509b80 (default 1)
--   VON_STAGE_FORCE_FROM   first forced frame (default 1600)
--   VON_STAGE_FORCE_TO     last forced frame (default 3000); FROM > TO reads
--                          the natural first match with no forcing
--   VON_STAGE_SECONDS      run length in emulated seconds (default 50)
--   VON_STAGE_TEXTURE_DUMP  optional directory to write the two texture RAMs
--   VON_STAGE_TEXTURE_FRAME frame at which to dump them (default near the end;
--                           0 dumps at SECONDS*60 - 60)

local LOG = assert(os.getenv("VON_STAGE_LOG"), "VON_STAGE_LOG required")
local ORD = tonumber(os.getenv("VON_STAGE_ORDINAL") or "0")
local FORCE_MIRROR = (os.getenv("VON_STAGE_FORCE_MIRROR") or "1") == "1"
local FROM = tonumber(os.getenv("VON_STAGE_FORCE_FROM") or "1600")
local TO = tonumber(os.getenv("VON_STAGE_FORCE_TO") or "3000")
local SECONDS = tonumber(os.getenv("VON_STAGE_SECONDS") or "50")
local TEXTURE_DUMP = os.getenv("VON_STAGE_TEXTURE_DUMP")
local TEXTURE_FRAME = tonumber(os.getenv("VON_STAGE_TEXTURE_FRAME") or "0")
if TEXTURE_FRAME <= 0 then TEXTURE_FRAME = SECONDS * 60 - 60 end
if TEXTURE_DUMP then os.execute("mkdir -p '" .. TEXTURE_DUMP .. "'") end
local SNAPSHOT = os.getenv("VON_STAGE_SNAPSHOT")
local PALETTE_DUMP = os.getenv("VON_STAGE_PALETTE_DUMP")
local dumped = false
local snapped = false
local palette_dumped = false
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

local function r(a)
	if not space then return -1 end
	local ok, v = pcall(function() return space:read_u32(a) end)
	return ok and v or -1
end

-- Dump one 1 MiB texture RAM (the sheet the renderer's get_texel reads) in the
-- same hex shape as scripts/trace-texture-buffers.sh publishes.
local function dump_bank(path, address, words)
	local f = assert(io.open(path, "w"))
	f:write(string.format("# address=%08x words=%x\n", address, words))
	for i = 0, words - 1 do
		f:write(string.format("%06x %04x\n", i, space:read_u16(address + i * 2)))
	end
	f:close()
end

local function dump_textures()
	if dumped or not TEXTURE_DUMP or not space then return end
	dumped = true
	dump_bank(TEXTURE_DUMP .. "/texture-11000000.hex", 0x11000000, 0x80000)
	dump_bank(TEXTURE_DUMP .. "/texture-11200000.hex", 0x11200000, 0x80000)
end

local function take_snapshot()
	if snapped or not SNAPSHOT then return end
	snapped = true
	local screen = manager.machine.screens[":screen"]
	if screen then
		pcall(function() screen:snapshot(SNAPSHOT) end)
	end
end

-- Dump the Model 2 palette pipeline (palette RAM, color-translation table, and
-- polygon luma RAM) in the same text shape render_texture_palette.parse_trace
-- reads, so an export can color the stage with the palette live at match time
-- (the geometry trace's write log caps out during boot).
local function dump_palette()
	if palette_dumped or not PALETTE_DUMP or not space then return end
	palette_dumped = true
	local f = assert(io.open(PALETTE_DUMP, "w"))
	for i = 0, 0x1fff do
		f:write(string.format(
			"vonj_palette_write: time=0.0 offset=%04x data=%04x mask=ffff value=%04x\n",
			i, space:read_u16(0x01800000 + i * 2) & 0xffff,
			space:read_u16(0x01800000 + i * 2) & 0xffff))
	end
	for i = 0, 0x5fff do
		f:write(string.format(
			"vonj_colorxlat_write: time=0.0 offset=%04x data=%04x mask=ffff value=%04x\n",
			i, space:read_u16(0x01810000 + i * 2) & 0xffff,
			space:read_u16(0x01810000 + i * 2) & 0xffff))
	end
	for i = 0, 0x1fff do
		f:write(string.format(
			"vonj_luma_write: time=0.0 offset=%04x data=%02x\n",
			i, space:read_u16(0x11400000 + i * 2) & 0xff))
	end
	f:close()
end

emu.register_periodic(function()
	frame = frame + 1
	if not space then
		local cpu = manager.machine.devices[":maincpu"]
		if cpu then space = cpu.spaces[":program"] or cpu.spaces["program"] end
	end
	setp("Coin 1", ":IN0", frame >= 900 and frame < 905)
	setp("1 Player Start", ":IN0", frame >= 1500 and frame < 1508)
	if space and frame >= FROM and frame <= TO then
		pcall(function()
			space:write_u32(0x503a80, ORD)
			if FORCE_MIRROR then
				space:write_u32(0x509b80, ORD)
			end
		end)
	end
	if space and frame % 30 == 0 then
		out:write(string.format(
			"f%d ord=%d a80=%x b80=%x a84=%x dbc=%x dc0=%x ca0=%08x cb0=%08x cc0=%08x banner=%08x\n",
			frame, ORD, r(0x503a80), r(0x509b80), r(0x503a84), r(0x504dbc), r(0x504dc0),
			r(0x504ca0), r(0x504cb0), r(0x504cc0), r(0x5770f0)))
		out:flush()
	end
	if frame >= TEXTURE_FRAME then
		dump_textures()
		dump_palette()
		take_snapshot()
	end
	if frame >= SECONDS * 60 then
		dump_textures()
		dump_palette()
		take_snapshot()
		out:close()
		manager.machine:exit()
	end
end)
