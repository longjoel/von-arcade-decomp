-- Upload the 0x49 state window and test vectors on both sides of its bound.

local frame = 0
local space
local log_file

local cases = {
    { name = "outside", vector = {0x40400000, 0x40800000, 0}, threshold = 0 },
    { name = "inside", vector = {0x3f800000, 0x40000000, 0x40000000}, threshold = 0 },
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function inject(case)
    word(0x00000008); word(0x00000048)
    for _, value in ipairs({0, 0, 0, 0x40800000, 0x40a00000}) do word(value) end
    word(0x00000008); word(0x00000049)
    for _, value in ipairs(case.vector) do word(value) end
    word(case.threshold)
    log("probe: case=" .. case.name)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_49_LOG") or
                "vonj-sharc-opcode-49-predicate.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then inject(cases[1]) end
    if frame == 1100 then inject(cases[2]) end
    if frame >= 1700 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
