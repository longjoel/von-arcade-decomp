-- Minimal autoboot script: insert one coin after the title, then stay on the
-- machine-select screen so its music can be captured with -wavwrite.
-- Used only for generating local reference captures; not part of the game.

local frame = 0
local in0, coin, start

emu.register_periodic(function()
	frame = frame + 1
	if not in0 then
		in0 = manager.machine.ioport.ports[":IN0"]
		if in0 then
			coin = in0.fields["Coin 1"]
			start = in0.fields["1 Player Start"]
		end
	end
	if not coin then
		return
	end
	-- Hold the coin briefly around frame 900 (the observed title duration).
	if frame >= 900 and frame < 915 then
		coin:set_value(1)
	else
		coin:clear_value()
	end
	-- Never confirm; remain on the select screen.
	if start then
		start:clear_value()
	end
end)
