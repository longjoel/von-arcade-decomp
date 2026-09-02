-- Measure opcode 0x34 with both signed helper fields active.

local frame = 0
local space
local log_file

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function header(opcode)
    word(0x00000008)
    word(opcode)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_34_COMBINED_LOG") or
                "vonj-sharc-opcode-34-combined.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 100 then
        header(0x10)
        header(0x34)
        word(0); word(0); word(0)
        word(0x4000); word(0x4000)
        word(0); word(0); word(0)
        header(0x11)
        log("probe: R5=R6=0x4000, R13/R14/R15=0")
    elseif frame >= 300 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
