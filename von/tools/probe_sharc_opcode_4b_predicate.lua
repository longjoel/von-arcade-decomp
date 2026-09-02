-- Seed the extended predicate state and exercise opcode 0x4b's normal path.

local frame = 0
local space
local log_file
local r2_bits = tonumber(os.getenv("VON_4B_R2") or "0")
local x_bits = tonumber(os.getenv("VON_4B_X") or "0")
local y_bits = tonumber(os.getenv("VON_4B_Y") or "0xc0800000")
local z_bits = tonumber(os.getenv("VON_4B_Z") or "0x3f800000")
local bound_bits = tonumber(os.getenv("VON_4B_BOUND") or "0")

local function log(message)
    if log_file then log_file:write(message .. "\n"); log_file:flush() end
end

local function word(value)
    space:write_u32(0x00884000, value)
end

local function upload_window()
    word(0x00000008); word(0x00000048)
    for _, value in ipairs({0, 0, 0, 0x40800000, 0x40a00000}) do word(value) end
end

local function run_case(case)
    local sharc = manager.machine.devices[":copro_adsp"]
    if sharc and sharc.state["R2"] then
        sharc.state["R2"].value = r2_bits
    end
    word(0x00000008); word(0x0000004b)
    for _, value in ipairs(case.vector) do word(value) end
    -- Keep the extra word available for the positive-Y fallback if selected.
    word(0)
    log("probe: case=" .. case.name)
end

local cases = {
    { name = "positive-y-fallback", vector = {0, 0x40800000, 0, 0} },
    { name = "negative-y-normal", vector = {x_bits, y_bits, z_bits, bound_bits} },
}

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_SHARC_4B_LOG") or
                "vonj-sharc-opcode-4b-predicate.log", "w"))
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
    if frame == 1100 then run_case(cases[2]) end
    if frame >= 1400 then
        log("probe: complete")
        if log_file then log_file:close() end
        manager.machine:exit()
    end
end)
