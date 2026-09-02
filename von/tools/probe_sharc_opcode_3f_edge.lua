-- Isolate opcode 0x3f edge behavior for its mixed integer/float quotient.

local frame = 0
local space
local log_file
local case_name = os.getenv("VON_3F_CASE") or "zero-zero"
local cases = {
    ["zero-zero"] = {0, 0, 0x40400000, 0x40800000},
    ["one-zero"] = {1, 0, 0x40400000, 0x40800000},
    ["negative-one"] = {0xffffffff, 1, 0x40400000, 0x40800000},
    ["int-min"] = {0x80000000, 1, 0x40400000, 0x40800000},
    ["nan-coefficient"] = {1, 1, 0x7fc00000, 0x40800000},
    ["inf-coefficient"] = {1, 1, 0x7f800000, 0x40800000},
}

local function word(value) space:write_u32(0x00884000, value) end
local function header(opcode) word(0x00000008); word(opcode) end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            log_file = assert(io.open(os.getenv("VON_3F_LOG") or
                "vonj-sharc-opcode-3f-edge.log", "w"))
            log_file:write("probe: start case=" .. case_name .. "\n")
        end
    end
    if not space then return end
    if frame == 600 then
        header(0x3f)
        for _, value in ipairs(cases[case_name] or cases["zero-zero"]) do word(value) end
        log_file:write("probe: case=" .. case_name .. "\n"); log_file:flush()
    end
    if frame >= 1000 then
        log_file:write("probe: complete\n"); log_file:close(); manager.machine:exit()
    end
end)
