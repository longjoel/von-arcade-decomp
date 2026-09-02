-- Probe opcode 0x4d's final comparison while varying only its fourth input.

local frame = 0
local space
local log_file
local threshold = tonumber(os.getenv("VON_4D_THRESHOLD") or "0")
local vector_name = os.getenv("VON_4D_VECTOR") or "3040"
local state3 = tonumber(os.getenv("VON_4D_STATE3") or "4")
local state3_bits = ({[2] = 0x40000000, [4] = 0x40800000, [8] = 0x41000000})[state3] or 0x40800000
local vectors = {
    x0 = {0, 0x40800000, 0},
    z0 = {0x40400000, 0x40800000, 0},
    x3z3 = {0x40400000, 0x40800000, 0x40400000},
    x4z0 = {0x40800000, 0x40800000, 0},
}
local vector = vectors[vector_name] or vectors.z0
local threshold_bits = ({
    [0] = 0x00000000,
    [1] = 0x3f800000,
    [2] = 0x40000000,
    [4] = 0x40800000,
    [8] = 0x41000000,
    [16] = 0x41800000,
})[threshold] or 0

local function word(value) space:write_u32(0x00884000, value) end
local function header(opcode) word(0x00000008); word(opcode) end

local function upload_window()
    header(0x48)
    for _, value in ipairs({0, 0, 0, state3_bits, 0x40a00000}) do word(value) end
end

local function upload_constants()
    header(0x44)
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_4D_LOG") or
                "vonj-sharc-opcode-4d-threshold.log", "w"))
            log_file:write("probe: start vector=" .. vector_name .. " threshold=" .. tostring(threshold) .. " state3=" .. tostring(state3) .. "\n")
        end
    end
    if not space then return end
    if frame == 600 then upload_window() end
    if frame == 720 then upload_constants() end
    if frame == 840 then
        header(0x4d)
        for _, value in ipairs({vector[1], vector[2], vector[3], threshold_bits}) do word(value) end
        log_file:write("probe: vector=" .. vector_name .. " threshold=" .. tostring(threshold) .. " state3=" .. tostring(state3) .. "\n")
        log_file:flush()
    end
    if frame >= 1400 then
        log_file:write("probe: complete\n"); log_file:close(); manager.machine:exit()
    end
end)
