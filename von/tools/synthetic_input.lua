-- Deterministic input stimulus for the Virtual-On MAME driver.
-- IN1 is active-low for player-one buttons and joystick bits.

local port
local fields
local field_names = {
    "Button 1",
    "Button 2",
    "Button 3",
    "Button 4",
    "Joystick Down",
    "Joystick Up",
    "Joystick Right",
    "Joystick Left",
}
local frame = 0

emu.register_periodic(function()
    frame = frame + 1

    port = port or manager.machine.ioport.ports["IN1"] or manager.machine.ioport.ports[":IN1"]
    if not port then
        return
    end
    fields = fields or {}
    for _, name in ipairs(field_names) do
        fields[name] = fields[name] or port.fields[name]
    end
    if not fields[field_names[1]] then
        return
    end

    local phase = math.floor((frame - 1) / 60)
    local active_name = field_names[(phase % #field_names) + 1]
    if frame % 60 == 1 then
        emu.print_info("synthetic phase " .. (phase + 1) .. ": " .. active_name)
    end
    for name, field in pairs(fields) do
        if field then
            if name == active_name and (frame % 60) < 30 then
                field:set_value(1)
            else
                field:clear_value()
            end
        end
    end

    if frame >= (#field_names * 60) then
        manager.machine:exit()
    end
end)
