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
    if frame % 10 == 0 then
        log(string.format("frame=%d init=%08x texture_status=%08x heartbeat=%08x done0=%04x bank1=%04x",
            frame,
            space:read_u32(0x00500090),
            space:read_u32(0x00500098),
            space:read_u32(0x00500094),
            space:read_u16(0x01000000 + 0x0323 * 2),
            space:read_u16(0x01000000 + 0x0359 * 2)))
    end
end)
