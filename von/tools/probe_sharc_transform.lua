-- Treat the SHARC as a function: inject one object-transform record and read
-- back the 12-word matrix it builds at DM(I7) where I7 = DM(0x30101).
--
-- Packet (recovered from i960 0x8dd40):
--   5, 47, c6, c8, c10, 22, c4, 21, c2, 20, c0, 58
-- opcodes 20/21/22 rotate the matrix by c0/c2/c4 (16-bit angle, 2*pi/65536);
-- opcode 47 computes translation = M * (c6,c8,c10); 58 commits.
--
-- Env: VON_SHARC_XF_LOG, VON_SHARC_XF_INJECT (frame), and C0..C10 overrides.

local function env(name, default)
    local v = os.getenv(name)
    return v and tonumber(v) or default
end

local LOG = os.getenv("VON_SHARC_XF_LOG") or "von-sharc-transform.log"
local INJECT = env("VON_SHARC_XF_INJECT", 1200)
local READING = INJECT + 60

local c = {}
for i = 0, 5 do c[i] = env("VON_REC_" .. i, 0) end
c[3], c[4], c[5] = env("VON_REC_3", 2000), env("VON_REC_4", 4000), env("VON_REC_5", 6000)

local frame = 0
local space, sharc, dspace, log_file
local ptr_before = nil

local function log(m)
    if log_file then log_file:write(m .. "\n"); log_file:flush() end
end

local function find_sharc()
    for _, dev in pairs(manager.machine.devices) do
        if dev.shortname == "adsp21062" then return dev end
    end
    return manager.machine.devices[":copro"]
end

local function s16(v)
    v = v & 0xffff
    if v >= 0x8000 then v = v - 0x10000 end
    return v
end

local function word(v) space:write_u32(0x00884000, v & 0xffffffff) end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then
            space = cpu.spaces[":program"] or cpu.spaces["program"]
            sharc = find_sharc()
            dspace = sharc and (sharc.spaces[":data"] or sharc.spaces["data"]
                     or sharc.spaces[":program"] or sharc.spaces["program"])
            log_file = assert(io.open(LOG, "w"))
            log("probe: sharc=" .. tostring(sharc) .. " data_space=" .. tostring(dspace))
        end
    end
    if not (space and dspace) then return end

    if frame == INJECT then
        ptr_before = dspace:read_u32(0x0030101)
        log(string.format("probe: ptr before=0x%08x", ptr_before))
        word(5)
        word(47); word(c[3]); word(c[4]); word(c[5])
        word(22); word(s16(c[2]))
        word(21); word(s16(c[1]))
        word(20); word(s16(c[0]))
        word(58)
        log(string.format("probe: injected c=%d,%d,%d,%d,%d,%d", c[0], c[1], c[2], c[3], c[4], c[5]))
    end

    if frame == READING then
        local ptr = dspace:read_u32(0x0030101)
        log(string.format("probe: matrix ptr now=0x%08x before=0x%08x", ptr, ptr_before))
        for _, base in ipairs({ ptr, ptr_before, 0x00030200, 0x00030230 }) do
            if base then
                log(string.format("probe: --- buffer 0x%08x ---", base))
                for i = 0, 11 do
                    log(string.format("probe:   [%02d]=0x%08x (%g)", i,
                        dspace:read_u32(base + i * 4),
                        dspace:read_u32(base + i * 4)))
                end
            end
        end
        log("probe: complete")
        log_file:close()
        manager.machine:exit()
    end
end)
