-- Upload the 0x4c state window and exercise its early and normal paths.

local frame = 0
local space
local log_file

local case = { name = "negative-y-fallback", vector = {0x40400000, 0xc0800000, 0}, threshold = 0x40c00000 }

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function inject()
    word(0x00000008); word(0x00000048)
    for _, value in ipairs({0, 0, 0, 0x40800000, 0x40a00000}) do word(value) end
    word(0x00000008); word(0x0000004c)
    for _, value in ipairs(case.vector) do word(value) end
    word(case.threshold)
    word(0)
    log("probe: case=" .. case.name)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_4C_LOG") or
                "vonj-sharc-opcode-4c-predicate.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then inject() end
    if frame >= 1400 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
