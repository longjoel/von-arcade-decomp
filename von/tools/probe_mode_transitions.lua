-- Ordered game-mode/phase fixture for the i960 host.
--
-- Logs every change of VON_GAME_MODE (0x5039f4), VON_MODE_PHASE (0x503a00),
-- the hardware-mode byte (0x503a08), and the mode-1 gating status bytes
-- (0x1d00034, 0x5023f2, 0x1d00038). For mode 1 it also decodes the 32-entry
-- phase table at 0x2b960 so the ordered handler targets are observable.
--
-- Env:
--   VON_MODE_LOG    output path (required)
--   VON_MODE_SECONDS run length for the header only (optional)

local out_path = assert(os.getenv("VON_MODE_LOG"), "VON_MODE_LOG required")
local seconds = tonumber(os.getenv("VON_MODE_SECONDS") or "0")
local out = assert(io.open(out_path, "w"))
out:write(string.format("# set=vonj seconds=%d\n", seconds))

local space = nil
local frame = 0
local last = {}

local function r32(address)
    local ok, value = pcall(function() return space:read_u32(address) end)
    return ok and value or 0
end

local function r8(address)
    local ok, value = pcall(function() return space:read_u8(address) end)
    return ok and value or 0
end

local function table_target(phase)
    local index = phase & 31
    local ok, value = pcall(function() return space:read_u32(0x2b960 + index * 4) end)
    return index, (ok and value or 0)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        space = cpu and cpu.spaces and (cpu.spaces[":program"] or cpu.spaces["program"])
        if not space then
            return
        end
    end
    local mode = r32(0x5039f4)
    local phase = r32(0x503a00)
    local hwmode = r8(0x503a08)
    local status34 = r32(0x1d00034)
    local status23f2 = r32(0x5023f2)
    local status38 = r32(0x1d00038)
    local key = string.format("%d/%d/%d/%d/%d/%d", mode, phase, hwmode,
        status34, status23f2, status38)
    if key == last.key then
        return
    end
    last.key = key
    local index, target = table_target(phase)
    out:write(string.format("f%d t=%.6f mode=%d phase=%d hw=%d s34=%d s23f2=%d s38=%d table[%d]=0x%08x\n",
        frame, emu.time(), mode, phase, hwmode, status34, status23f2, status38,
        index, target))
    out:flush()
end)
