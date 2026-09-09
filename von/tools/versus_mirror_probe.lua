-- Versus mirror attempt, timed so the battle lands in the geometry trace
-- window (machine time 138-172s): coin ~120s, 2P start, default selects,
-- snapshots at select + battle, P1 driven once the fight starts.
local frame = 0

local function field(port, name)
    local p = manager.machine.ioport.ports[port]
    return p and p.fields[name] or nil
end

local F = {
    coin = field(":IN0", "Coin 1"),
    start2 = field(":IN0", "2 Players Start"),
    p1right = field(":IN1", "P1 Left Stick/Right"),
    p1dash = field(":IN1", "P1 Left Dash"),
}
assert(F.coin and F.start2 and F.p1right and F.p1dash, "required input fields unavailable")

local pressed_until = {}
local function press(name, duration)
    F[name]:set_value(1)
    pressed_until[name] = frame + duration
end

local function snap(name)
    pcall(function() manager.machine.video:snapshot() end)
end

emu.register_periodic(function()
    frame = frame + 1
    for name, until_frame in pairs(pressed_until) do
        if frame >= until_frame then
            F[name]:clear_value()
            pressed_until[name] = nil
        end
    end
    if frame == 7200 then press("coin", 8) end
    if frame == 7260 then press("coin", 8) end
    if frame == 7400 then press("start2", 10) end
    if frame == 8300 then snap("select") end
    if frame == 9500 then snap("battle") end
    if frame >= 9600 and frame < 10700 then
        F.p1right:set_value(1)
        if frame % 120 < 30 then F.p1dash:set_value(1) else F.p1dash:clear_value() end
    end
    if frame == 10700 then snap("driven") end
    if frame >= 11100 then manager.machine:exit() end
end)
