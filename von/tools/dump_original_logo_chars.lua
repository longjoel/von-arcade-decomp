-- Dump the character RAM used by the captured SEGA/title tile IDs.
local cpu = assert(manager.machine.devices[":maincpu"])
local space = assert(cpu.spaces[":program"] or cpu.spaces["program"])
local output_path = os.getenv("VON_LOGO_CHAR_DUMP") or "vonj-logo-char.hex"
local palette_path = os.getenv("VON_LOGO_PALETTE_DUMP")
local tile_path = os.getenv("VON_LOGO_TILE_DUMP")
local target_frame = tonumber(os.getenv("VON_LOGO_CHAR_FRAME") or "900")
local frame = 0
local done = false

local function dump()
    if done then return end
    done = true
    local output = assert(io.open(output_path, "w"))
    output:write(string.format("# frame=%d\n", frame))
    -- Tile IDs 0x0082..0x0183 address this character-RAM window.
    for address = 0, 0x3fff, 2 do
        output:write(string.format("%04x %04x\n", address,
            space:read_u16(0x01080000 + address)))
    end
    output:close()
    if palette_path then
        local palette = assert(io.open(palette_path, "w"))
        palette:write(string.format("# frame=%d\n", frame))
        for offset = 0, 0x3ff do
            palette:write(string.format("%04x %04x\n", offset,
                space:read_u16(0x01800000 + offset * 2)))
        end
        palette:close()
    end
    if tile_path then
        local tile = assert(io.open(tile_path, "w"))
        tile:write(string.format("# frame=%d\n", frame))
        for offset = 0, 0x0fff do
            tile:write(string.format("%04x %04x\n", offset,
                space:read_u16(0x01000000 + offset * 2)))
        end
        tile:close()
    end
    manager.machine:exit()
end

emu.register_periodic(function()
    frame = frame + 1
    if frame >= target_frame then dump() end
end)
