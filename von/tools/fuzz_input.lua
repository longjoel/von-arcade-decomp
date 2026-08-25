-- Seeded, bounded Virtual-On input fuzzer.
-- Use VON_FUZZ_SEED to reproduce a run exactly.

local seed = tonumber(os.getenv("VON_FUZZ_SEED") or "1") or 1
local frame = 0
local state = seed % 2147483647
local ports
local fields
local coin
local start

local function next_random()
    state = (state * 48271) % 2147483647
    return state
end

local function get_field(port, names)
    for _, name in ipairs(names) do
        local field = port.fields[name]
        if field then
            return field
        end
    end
    return nil
end

emu.print_info("input fuzz seed: " .. seed)

emu.register_periodic(function()
    frame = frame + 1
    if not ports then
        local in0 = manager.machine.ioport.ports["IN0"] or manager.machine.ioport.ports[":IN0"]
        local in1 = manager.machine.ioport.ports["IN1"] or manager.machine.ioport.ports[":IN1"]
        local in2 = manager.machine.ioport.ports["IN2"] or manager.machine.ioport.ports[":IN2"]
        if not in0 or not in1 or not in2 then
            return
        end
        ports = {in0, in1, in2}
        coin = get_field(in0, {"Coin 1"})
        start = get_field(in0, {"1 Player Start", "Start 1"})
    end

    fields = fields or {
        get_field(ports[2], {"P1 Left Shot", "Button 1"}),
        get_field(ports[2], {"P1 Left Dash", "Button 2"}),
        get_field(ports[2], {"P1 Left Stick/Down", "Joystick Down"}),
        get_field(ports[2], {"P1 Left Stick/Up", "Joystick Up"}),
        get_field(ports[2], {"P1 Left Stick/Right", "Joystick Right"}),
        get_field(ports[2], {"P1 Left Stick/Left", "Joystick Left"}),
        get_field(ports[3], {"P1 Right Shot", "Button 3"}),
        get_field(ports[3], {"P1 Right Dash", "Button 4"}),
        get_field(ports[3], {"P1 Right Stick/Down", "Joystick Down"}),
        get_field(ports[3], {"P1 Right Stick/Up", "Joystick Up"}),
        get_field(ports[3], {"P1 Right Stick/Right", "Joystick Right"}),
        get_field(ports[3], {"P1 Right Stick/Left", "Joystick Left"}),
    }
    if frame == 1 then
        local available = 0
        for _, field in ipairs(fields) do
            if field then
                available = available + 1
            end
        end
        emu.print_info("input fuzz fields available: " .. available .. "/" .. #fields)
        emu.print_info("coin field: " .. (coin and "yes" or "no"))
        emu.print_info("start field: " .. (start and "yes" or "no"))
    end

    if coin then
        if frame <= 10 then coin:set_value(1) else coin:clear_value() end
    end
    if start then
        if frame >= 60 and frame < 70 then start:set_value(1) else start:clear_value() end
    end

    -- Hold each random control state for four frames to exercise transitions
    -- without making the trace depend on the emulator's callback frequency.
    if frame % 4 == 1 then
        local mask = next_random()
        for index, field in ipairs(fields) do
            if field then
                if (mask % (2 ^ index)) >= (2 ^ (index - 1)) then
                    field:set_value(1)
                else
                    field:clear_value()
                end
            end
        end
    end

    if frame >= 600 then
        manager.machine:exit()
    end
end)
