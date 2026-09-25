-- Insert one coin after the attract warmup, then hand full control to the
-- player. Used for manual select-screen captures: the operator cycles fighters.

local frame = 0
local coin

emu.register_periodic(function()
	frame = frame + 1
	if not coin then
		local in0 = manager.machine.ioport.ports[":IN0"]
		if in0 then
			coin = in0.fields["Coin 1"]
		end
	end
	if coin then
		if frame >= 900 and frame < 910 then
			coin:set_value(1)
		else
			coin:clear_value()
		end
	end
end)
