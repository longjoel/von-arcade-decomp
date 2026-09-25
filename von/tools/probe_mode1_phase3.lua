-- Per-frame window around the mode-1 phase-3 handler (0x2b810) transition.
-- Logs the words the handler writes (0x503a04, 0x504d28, 0x504d30, 0x100a004)
-- with the mode/phase so the runtime effect can be tied to the listing.
--
-- Env:
--   VON_PHASE3_LOG  output path (required)
--   VON_PHASE3_FROM / VON_PHASE3_TO  emulated-time window (default 15.7 / 16.2)

local out_path = assert(os.getenv("VON_PHASE3_LOG"), "VON_PHASE3_LOG required")
local from = tonumber(os.getenv("VON_PHASE3_FROM") or "15.7")
local to = tonumber(os.getenv("VON_PHASE3_TO") or "16.2")
local out = assert(io.open(out_path, "w"))
out:write(string.format("# mode1 phase3 window %.3f..%.3f\n", from, to))

local space = nil

local function r32(address)
    local ok, value = pcall(function() return space:read_u32(address) end)
    return ok and value or 0
end

emu.register_periodic(function()
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        space = cpu and cpu.spaces and (cpu.spaces[":program"] or cpu.spaces["program"])
        if not space then
            return
        end
    end
    local now = emu.time()
    if now >= from and now <= to then
        out:write(string.format("t=%.6f mode=%u phase=%u a04=%08x d28=%08x d30=%08x v004=%08x\n",
            now, r32(0x5039f4), r32(0x503a00), r32(0x503a04), r32(0x504d28),
            r32(0x504d30), r32(0x100a004)))
        out:flush()
    end
end)
