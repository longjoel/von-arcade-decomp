-- Per-frame object field probe for the i960 frame-step / heading recovery.
--
-- Logs the frame-step state and heading fields of both mech objects every
-- frame, so the 0x371e0 prefix (heading/facing 16.16 integrator) and the
-- state-1/11/19/20/22 gate tails can be fitted against original execution
-- rather than decoded blind.
--
--   VON_FRAME_LOG=out.log VON_FRAME_SECONDS=40 ./bin/vonctl run -video none \
--     -sound none -skip_gameinfo -seconds_to_run 40 \
--     -autoboot_script von/tools/probe_framestep_fields.lua
--
-- One line per object per frame; values are raw (halfwords unsigned, floats
-- as their IEEE-754 bit patterns).

local SECONDS = tonumber(os.getenv("VON_FRAME_SECONDS") or "40")
local LOG_PATH = os.getenv("VON_FRAME_LOG") or "von-framestep-fields.log"
local WRITE_LOG_PATH = os.getenv("VON_FRAME_WRITE_LOG")
local START_FRAME = tonumber(os.getenv("VON_FRAME_START") or "0")

local PLAYER = 0x00503ad0
local CPU = 0x005040d0
local GAME_MODE = 0x005039f4
local MODE_PHASE = 0x00503a00

local U16_FIELDS = {
    0x00, 0x02, 0x2c, 0x2e, 0x32, 0x34, 0x36, 0x38, 0x3a, 0x3c, 0x46, 0x4e,
    0x102, 0x10e, 0x170, 0x172, 0x174, 0x176, 0x178, 0x17a, 0x17c, 0x17e,
    0x180, 0x184, 0x186, 0x188, 0x18e, 0x198, 0x1a0, 0x1b2, 0x1e2
}
local U8_FIELDS = {
    0x136, 0x137, 0x138, 0x139, 0x13a, 0x13b, 0x13c, 0x13d, 0x13e, 0x13f,
    0x142, 0x143, 0x1a8, 0x1a9, 0x1db, 0x1dc
}
local U32_FIELDS = {
    0x04, 0x08, 0x0c, 0x10, 0x64, 0x6c, 0x74, 0x150, 0x1c4, 0x1c8, 0x1cc
}

local file = assert(io.open(LOG_PATH, "w"))
local write_file = WRITE_LOG_PATH and assert(io.open(WRITE_LOG_PATH, "w")) or nil
local frame = 0
local space
local cpu_device

local function setup()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then
        return false
    end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    cpu_device = cpu
    return space ~= nil
end

-- Instruction-level write taps for the frame-step fields. The tap runs at the
-- writing instruction, so CURPC names the exact producer and separates the
-- 0x371e0 prefix (0x372ac/0x37320/0x3734c) from the 0x32560 backbone handlers.
-- Tap handles must be retained; an unreferenced MAME Lua tap is collected.
local taps = {}

local function install_write_taps(base, label)
    local windows = { { 0x30, 8 }, { 0x184, 4 }, { 0x194, 12 } }
    for _, window in ipairs(windows) do
        local lo, size, tag = window[1], window[2], label
        local name = string.format("von-fs-%s-%x", tag, lo)
        local ok, tap = pcall(function()
            return space:install_write_tap(base + lo, base + lo + size - 1, name,
                function(offset, data, mask)
                    local pc = 0
                    pcall(function()
                        pc = cpu_device.state["CURPC"].value
                    end)
                    write_file:write(string.format(
                        "w frame=%d obj=%s off=%x pc=%08x data=%x mask=%x\n",
                        frame, tag, offset - base, pc, data, mask))
                    return data
                end)
        end)
        if ok then
            taps[#taps + 1] = tap
        end
        write_file:write(string.format("w installed obj=%s off=%x ok=%s err=%s\n",
            label, lo, tostring(ok), tostring(tap)))
    end
end

-- Sanity tap: the marker-slot window that gameplay_progress.lua already logs.
local function install_marker_probe()
    local ok, tap = pcall(function()
        return space:install_write_tap(0x00562430, 0x00562477, "von-fs-marker-probe",
            function(offset, data, mask)
                write_file:write(string.format(
                    "w marker frame=%d off=%x data=%x\n", frame, offset, data))
                return data
            end)
    end)
    if ok then
        taps[#taps + 1] = tap
    end
    write_file:write(string.format("w marker-install ok=%s err=%s\n",
        tostring(ok), tostring(tap)))
end

local function read_u16(address)
    local ok, value = pcall(function() return space:read_u16(address) end)
    return ok and value or 0xffff
end

local function read_u8(address)
    local ok, value = pcall(function() return space:read_u8(address) end)
    return ok and value or 0xff
end

local function read_u32(address)
    local ok, value = pcall(function() return space:read_u32(address) end)
    return ok and value or 0xffffffff
end

local function dump_object(label, base)
    local parts = { string.format("frame=%d obj=%s", frame, label) }
    for _, offset in ipairs(U16_FIELDS) do
        parts[#parts + 1] = string.format("%x=%04x", offset, read_u16(base + offset))
    end
    for _, offset in ipairs(U8_FIELDS) do
        parts[#parts + 1] = string.format("%x=%02x", offset, read_u8(base + offset))
    end
    for _, offset in ipairs(U32_FIELDS) do
        parts[#parts + 1] = string.format("%x=%08x", offset, read_u32(base + offset))
    end
    file:write(table.concat(parts, " ") .. "\n")
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        if frame % 60 == 1 then
            if setup() and write_file then
                install_write_taps(PLAYER, "player")
                install_write_taps(CPU, "cpu")
                install_marker_probe()
            end
        end
        return
    end
    if write_file then
        write_file:flush()
    end
    if frame < START_FRAME then
        return
    end
    if frame % 60 == 0 then
        file:write(string.format(
            "frame=%d mode=%08x phase=%08x\n", frame,
            read_u32(GAME_MODE), read_u32(MODE_PHASE)))
    end
    dump_object("player", PLAYER)
    dump_object("cpu", CPU)
    if frame >= SECONDS * 60 then
        file:flush()
        manager.machine:exit()
    end
end)
