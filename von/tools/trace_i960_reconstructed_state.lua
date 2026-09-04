-- Report milestones from the reconstructed i960 host path.

local log_path = os.getenv("VON_I960_STATE_LOG") or "i960-reconstructed-state.log"
local log_file = assert(io.open(log_path, "w"))
local cpu = manager.machine.devices[":maincpu"]
local space = cpu.spaces["program"]
local frame = 0

local function log(message)
    log_file:write(message .. "\n")
    log_file:flush()
end

emu.register_periodic(function()
    frame = frame + 1
    if frame == 60 then
        pcall(function() manager.machine.video:snapshot() end)
    end
    if frame % 10 == 0 then
        log(string.format("frame=%d render_mode=%08x videoctl=%08x init=%08x texture_status=%08x heartbeat=%08x attract_tick=%08x transition=%08x loader=%08x done0=%04x bank1=%04x",
            frame,
            space:read_u32(0x10000000),
            space:read_u32(0x0098000c),
            space:read_u32(0x00500090),
            space:read_u32(0x00500098),
            space:read_u32(0x00500094),
            space:read_u32(0x0050009c),
            space:read_u32(0x005000a0),
            space:read_u32(0x00504d98),
            space:read_u16(0x01000000 + 0x0323 * 2),
            space:read_u16(0x01000000 + 0x0359 * 2)))
        if frame == 60 then
            log(string.format("char_ram=%08x,%08x,%08x,%08x glyph49=%08x,%08x char_81000=%08x,%08x source60=%08x sourcea0=%08x palette0=%04x,%04x,%04x,%04x palette10=%04x,%04x,%04x,%04x lookup=%04x,%04x,%04x,%04x,%04x,%04x tilectl=%04x,%04x,%04x,%04x tile=%04x,%04x",
                space:read_u32(0x01080000), space:read_u32(0x01080004),
                space:read_u32(0x01080008), space:read_u32(0x0108000c),
                space:read_u32(0x01080000 + 0x49 * 32), space:read_u32(0x01080004 + 0x49 * 32),
                space:read_u32(0x01081000), space:read_u32(0x01081004),
                space:read_u32(0x02e60bb8), space:read_u32(0x02ea0bb8),
                space:read_u16(0x01800000), space:read_u16(0x01800002),
                space:read_u16(0x01800004), space:read_u16(0x01800006),
                space:read_u16(0x01800020), space:read_u16(0x01800022),
                space:read_u16(0x01800024), space:read_u16(0x01800026),
                space:read_u16(0x01810080), space:read_u16(0x01815080),
                space:read_u16(0x01818080), space:read_u16(0x01800002),
                space:read_u16(0x01800022), space:read_u16(0x01800000),
                space:read_u16(0x0100a000), space:read_u16(0x0100a008),
                space:read_u16(0x0100a010), space:read_u16(0x0100a018),
                space:read_u16(0x01000000 + 0x0308 * 2),
                space:read_u16(0x01000000 + 0x1308 * 2)))
        end
    end
end)
