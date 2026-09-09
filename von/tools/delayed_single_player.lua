-- Delayed single-player: coin/start/select late so the battle lands in the
-- geometry trace window (machine time 138-172s). P1 mech = SELECT_STEPS
-- right-presses from the default cursor.
local SELECT_STEPS = tonumber(os.getenv("VON_SELECT_STEPS") or "0")
local frame = 0

local function field(port, name)
    local p = manager.machine.ioport.ports[port]
    return p and p.fields[name] or nil
end

local F = {
    coin = field(":IN0", "Coin 1"),
    start = field(":IN0", "1 Player Start"),
    right = field(":IN1", "P1 Left Stick/Right"),
}
assert(F.coin and F.start and F.right, "required input fields unavailable")

local pressed_until = {}
local function press(name, duration)
    F[name]:set_value(1)
    pressed_until[name] = frame + duration
end

local steps_done = 0
emu.register_periodic(function()
    frame = frame + 1
    for name, until_frame in pairs(pressed_until) do
        if frame >= until_frame then
            F[name]:clear_value()
            pressed_until[name] = nil
        end
    end
    if frame == 7800 then press("coin", 8) end
    if frame == 8100 then press("start", 8) end
    if steps_done < SELECT_STEPS and frame >= 8300 + steps_done * 45 then
        press("right", 8)
        steps_done = steps_done + 1
    end
    if frame == 8300 + SELECT_STEPS * 45 + 120 then press("start", 8) end
    if frame == 8300 + SELECT_STEPS * 45 + 140 then
        pcall(function() manager.machine.video:snapshot() end)
    end
    if frame >= 11200 then manager.machine:exit() end
end)
