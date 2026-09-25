-- Snapshot the original game at chosen frames while optionally driving the
-- boot/select flow. Reference frames for side-by-side comparison with Godot.
--
-- Env:
--   VON_SNAP_DIR        output dir (default /tmp/von-snaps)
--   VON_SNAP_FRAMES     comma-separated frame numbers to snap
--   VON_SNAP_COIN_FRAME default 900
--   VON_SNAP_START_FRAME  -1 to stay on select; else press Start
--   VON_SNAP_STEPS      number of right presses to move the selector
--   VON_SNAP_STEP_FRAMES  spacing between selector presses (default 90)
--   VON_SNAP_HOLD       frames to hold a press (default 18)

local DIR = os.getenv("VON_SNAP_DIR") or "/tmp/von-snaps"
local FRAMES = os.getenv("VON_SNAP_FRAMES") or ""
local COIN_FRAME = tonumber(os.getenv("VON_SNAP_COIN_FRAME") or "900")
local START_FRAME = tonumber(os.getenv("VON_SNAP_START_FRAME") or "-1")
local STEPS = tonumber(os.getenv("VON_SNAP_STEPS") or "0")
local STEP_FRAMES = tonumber(os.getenv("VON_SNAP_STEP_FRAMES") or "90")
local HOLD = tonumber(os.getenv("VON_SNAP_HOLD") or "18")

local targets = {}
for tok in string.gmatch(FRAMES, "([^,]+)") do
    targets[#targets + 1] = tonumber(tok)
end
os.execute("mkdir -p '" .. DIR .. "'")

local frame = 0
local coin, start, right
local snap_idx = 1

local function setup()
    local ports = manager.machine.ioport.ports
    local in0 = ports[":IN0"]
    local in1 = ports[":IN1"]
    if not (in0 and in1) then
        return false
    end
    coin = in0.fields["Coin 1"]
    start = in0.fields["1 Player Start"]
    right = in1.fields["P1 Left Stick/Right"]
    return coin ~= nil
end

local function pulse(field, on)
    if not field then return end
    if on then field:set_value(1) else field:clear_value() end
end

emu.register_periodic(function()
    frame = frame + 1
    if not coin then
        if not setup() then return end
    end

    pulse(coin, frame >= COIN_FRAME and frame < COIN_FRAME + 10)
    if START_FRAME > 0 then
        pulse(start, frame >= START_FRAME and frame < START_FRAME + 10)
    end
    local base = START_FRAME > 0 and (START_FRAME - 420) or (COIN_FRAME + 200)
    local moving = false
    for s = 1, STEPS do
        local f = base + s * STEP_FRAMES
        if frame >= f and frame < f + HOLD then moving = true end
    end
    pulse(right, moving)

    while snap_idx <= #targets and frame >= targets[snap_idx] do
        local screen = manager.machine.screens[":screen"]
        if screen then
            local path = string.format("%s/frame-%05d.png", DIR, frame)
            pcall(function() screen:snapshot(path) end)
            emu.print_info("snapshot " .. path)
        end
        snap_idx = snap_idx + 1
    end
end)
