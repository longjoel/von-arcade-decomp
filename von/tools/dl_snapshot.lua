-- Display-list snapshot probe: dump a device RAM window at given frames.
--
-- Used to capture stage-geometry swaps across round/match transitions
-- during -playback. The von display list window at 0x00900000 is outside
-- work RAM, so the gameplay snapshot path never covers it.
--
-- Environment: VON_DL_FRAMES (comma-separated frame numbers)
--              VON_DL_PATH   (output prefix; suffixed -<frame>.bin)
--              VON_DL_BASE   (default 0x00900000)
--              VON_DL_LEN    (default 0x20000 words)
--              VON_DL_SECONDS (default 230 emulated seconds)

local SECONDS = tonumber(os.getenv("VON_DL_SECONDS") or "230")
local TARGET_FRAMES = SECONDS * 60
local PATH = os.getenv("VON_DL_PATH") or "vonj-display-list"
local BASE = tonumber(os.getenv("VON_DL_BASE") or "0x00900000")
local LEN = tonumber(os.getenv("VON_DL_LEN") or "0x20000")

local frames_raw = os.getenv("VON_DL_FRAMES") or ""
local frames = {}
for tok in string.gmatch(frames_raw, "([^,]+)") do
    frames[#frames + 1] = tonumber(tok)
end

local log_file = assert(io.open(PATH .. ".log", "w"))

local function log(msg)
    log_file:write(msg .. "\n")
    log_file:flush()
end

local frame = 0
local space = nil
local done = {}

local function setup()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then
        return false
    end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    return space ~= nil
end

local function dump(tag)
    local path = string.format("%s-%d.bin", PATH, tag)
    local out = assert(io.open(path, "wb"))
    for offset = 0, LEN - 1 do
        local ok, word = pcall(function()
            return space:read_u32(BASE + offset * 4)
        end)
        local w = (ok and type(word) == "number") and word or 0
        out:write(string.char(
            w & 0xff, (w >> 8) & 0xff,
            (w >> 16) & 0xff, (w >> 24) & 0xff))
        if offset % 0x8000 == 0 then
            out:flush()
        end
    end
    out:close()
    log(string.format("dl: dumped frame %d to %s", frame, path))
end

emu.register_periodic(function()
    frame = frame + 1
    if not space and frame % 60 == 1 then
        if not setup() then
            return
        end
    end
    if not space then
        return
    end
    for _, want in ipairs(frames) do
        if frame == want and not done[want] then
            done[want] = true
            dump(want)
        end
    end
    if frame >= TARGET_FRAMES then
        log("dl: session complete at frame " .. frame)
        manager.machine:exit()
    end
end)
