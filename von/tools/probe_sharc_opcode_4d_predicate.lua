-- Seed the extended predicate state and exercise opcode 0x4d's two branches.

local frame = 0
local space
local log_file

local cases = {
    { name = "positive-y-normal", vector = {0, 0x40800000, 0, 0}, extra = false },
}

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function upload_window()
    word(0x00000008); word(0x00000048)
    for _, value in ipairs({0, 0, 0, 0xc2c80000, 0x40a00000}) do word(value) end
end

local function run_case(case)
    word(0x00000008); word(0x0000004d)
    for _, value in ipairs(case.vector) do word(value) end
    if case.extra then word(0) end
    log("probe: case=" .. case.name)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_4D_LOG") or
                "vonj-sharc-opcode-4d-predicate.log", "w"))
            log("probe: start")
        end
    end
    if not space then return end
    if frame == 600 then upload_window() end
    if frame == 720 then
        word(0x00000008); word(0x00000044)
        log("probe: initialized extended predicate constants")
    end
    if frame == 840 then run_case(cases[1]) end
    if frame >= 1550 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
