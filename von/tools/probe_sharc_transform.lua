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
-- RESET writes an identity 3x4 to 0x30200 and points DM(0x30101) there before
-- injecting, so the packet's pure rotation is observable (the motion packet
-- pre-multiplies the existing matrix, otherwise contaminated by game state).
local RESET = os.getenv("VON_SHARC_XF_RESET") == "1"
local MATRIX_PTR = 0x0030101
local MATRIX_BASE = 0x00030200

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

local function dump(tag, base)
    local vals = {}
    for i = 0, 11 do
        -- SHARC data-space addresses are word-addressed (the gameplay tap
        -- and matrix_at helper use the same convention).
        vals[i + 1] = string.format("%08x", dspace:read_u32(base + i))
    end
    log(string.format("%s base=0x%08x %s", tag, base, table.concat(vals, " ")))
end

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

    if frame == INJECT - 1 and os.getenv("VON_SHARC_XF_TAP") == "1" then
        pcall(function()
            dspace:install_write_tap(MATRIX_BASE, MATRIX_BASE + 0x2c, "xftap",
                function(offset, data, mask)
                    local pc = sharc.state["PC"] and sharc.state["PC"].value
                    log(string.format("tap f=%d pc=%s off=%08x data=%08x mask=%08x",
                        frame, pc and string.format("0x%x", pc) or "?",
                        offset, data, mask))
                    return data
                end)
            log("probe: matrix write tap installed")
        end)
    end

    if frame == INJECT then
        if RESET then
            local id = { 0x3f800000, 0, 0, 0, 0x3f800000, 0, 0, 0, 0x3f800000, 0, 0, 0 }
            for i = 0, 11 do
                dspace:write_u32(MATRIX_BASE + i, id[i + 1])
            end
            dspace:write_u32(MATRIX_PTR, MATRIX_BASE)
            log(string.format("probe: reset matrix->identity at 0x%08x", MATRIX_BASE))
        end
        ptr_before = dspace:read_u32(0x0030101)
        log(string.format("probe: ptr before=0x%08x", ptr_before))
        -- Recovered batch-packet handshake (recovered_geometry_batch_packet_8d400):
        -- control, record window, then the FIFO packet.
        space:write_u32(0x00800010, 0x101)
        space:write_u32(0x00804000, 0)
        space:write_u32(0x00804004, 0)
        space:write_u32(0x00804008, 0)
        space:write_u32(0x0080400c, 0)
        word(5)
        word(47); word(c[3]); word(c[4]); word(c[5])
        word(22); word(s16(c[2]))
        word(21); word(s16(c[1]))
        word(20); word(s16(c[0]))
        word(58)
        log(string.format("probe: injected c=%d,%d,%d,%d,%d,%d", c[0], c[1], c[2], c[3], c[4], c[5]))
    end

    if frame >= INJECT and frame <= INJECT + 6 then
        local ptr = dspace:read_u32(0x0030101)
        log(string.format("probe: frame=%d ptr=0x%08x", frame, ptr))
        dump("  at_ptr", ptr)
        dump("  at_30200", 0x00030200)
    end
    if frame == INJECT + 7 then
        log("probe: complete")
        log_file:close()
        manager.machine:exit()
    end
end)
