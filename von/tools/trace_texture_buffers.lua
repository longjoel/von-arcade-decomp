-- Capture texture decompressor headers and output banks from the original ROM.

local LOG_PATH = os.getenv("VON_TEXTURE_LOG") or "texture-buffers.log"
local DUMP_DIR = os.getenv("VON_TEXTURE_DUMP_DIR") or "."
local frame = 0
local dumps = 0
local last_marker = nil
local cpu = manager.machine.devices[":maincpu"]
local space = cpu.spaces["program"]
local log_file = assert(io.open(LOG_PATH, "w"))

local function be32(address)
    return (space:read_u8(address) << 24) |
        (space:read_u8(address + 1) << 16) |
        (space:read_u8(address + 2) << 8) |
        space:read_u8(address + 3)
end

local function log(message)
    log_file:write(message .. "\n")
    log_file:flush()
end

local function dump_bank(path, address, words)
    local output = assert(io.open(path, "w"))
    output:write(string.format("# address=%08x words=%x\n", address, words))
    for index = 0, words - 1 do
        output:write(string.format("%06x %04x\n", index,
            space:read_u16(address + index * 2)))
    end
    output:close()
end

local source0 = 0x02c00008
local source1 = 0x02c77438
local header0 = be32(source0)
local header1 = be32(source1)
local words0 = header0 >> 1
local words1 = header1 >> 1
log(string.format("header0=%08x words0=%x", header0, words0))
log(string.format("header1=%08x words1=%x", header1, words1))
local source_bytes0 = {}
local source_bytes1 = {}
for index = 0, 31 do
    source_bytes0[#source_bytes0 + 1] = string.format("%02x", space:read_u8(source0 + index))
    source_bytes1[#source_bytes1 + 1] = string.format("%02x", space:read_u8(source1 + index))
end
log("source0=" .. table.concat(source_bytes0))
log("source1=" .. table.concat(source_bytes1))

emu.register_periodic(function()
    frame = frame + 1
    if frame % 30 == 0 and dumps < 4 then
        local hash = 2166136261
        local hash2 = 2166136261
        for index = 0, 0x3ff do
            hash = (hash ~ space:read_u16(0x11000000 + index * 2)) *
                16777619 % 4294967296
            hash2 = (hash2 ~ space:read_u16(0x11200000 + index * 2)) *
                16777619 % 4294967296
        end
        local marker = string.format("%08x:%08x", hash, hash2)
        if marker ~= last_marker then
            last_marker = marker
            log("dump_frame=" .. frame .. " marker=" .. marker)
            dump_bank(DUMP_DIR .. "/texture-11000000." .. dumps .. ".hex",
                0x11000000, words0)
            dump_bank(DUMP_DIR .. "/texture-11200000." .. dumps .. ".hex",
                0x11200000, words0)
            dumps = dumps + 1
        end
    end
    if frame >= 600 then
        log_file:close()
        manager.machine:exit()
    end
end)
