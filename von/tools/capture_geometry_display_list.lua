local output_path = os.getenv("VON_DISPLAY_LIST_DUMP") or "/tmp/von-display-list.bin"
local cpu = manager.machine.devices[":maincpu"]
local space = cpu.spaces["program"]
local fields = manager.machine.ioport.ports[":IN0"].fields
local frame = 0
local dumped = false

local pressed_until = {}
local function press(name, duration)
    fields[name]:set_value(1)
    pressed_until[name] = frame + duration
end

local function dump()
    local file = assert(io.open(output_path, "wb"))
    for offset = 0, 0x1ffff, 4 do
        local word = space:read_u32(0x00900000 + offset)
        file:write(string.char(
            word & 0xff, (word >> 8) & 0xff,
            (word >> 16) & 0xff, (word >> 24) & 0xff))
    end
    file:close()
end

emu.register_periodic(function()
    frame = frame + 1
    for name, until_frame in pairs(pressed_until) do
        if frame >= until_frame then
            fields[name]:clear_value()
            pressed_until[name] = nil
        end
    end
    if frame == 900 then press("Coin 1", 8) end
    if frame == 1500 then press("1 Player Start", 8) end
    if frame == 2400 and not dumped then
        dump()
        dumped = true
    end
    if frame >= 2460 then manager.machine:exit() end
end)
