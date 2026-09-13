-- Differential SHARC calibration: dump the matrix region before and after one
-- injected packet (5,47,c,c,c,22,c,21,c,20,c,58) so the effect is unambiguous.
--
-- Env: VON_SHARC_CAL_LOG, VON_SHARC_CAL_INJECT, VON_REC_0..5.

local function env(name, default)
    local v = os.getenv(name)
    return v and tonumber(v) or default
end

local LOG = os.getenv("VON_SHARC_CAL_LOG") or "von-sharc-calib.log"
local INJECT = env("VON_SHARC_CAL_INJECT", 1200)
local BASE = 0x0030100
local WORDS = 0x180

local c = {}
for i = 0, 5 do c[i] = env("VON_REC_" .. i, 0) end

local frame = 0
local space, sharc, dspace, log_file

local function log(m)
    if log_file then log_file:write(m .. "\n"); log_file:flush() end
end

local function find_sharc()
    for _, dev in pairs(manager.machine.devices) do
        if dev.shortname == "adsp21062" then return dev end
    end
    return nil
end

local function s16(v)
    v = v & 0xffff
    if v >= 0x8000 then v = v - 0x10000 end
    return v
end

local function word(v) space:write_u32(0x00884000, v & 0xffffffff) end

local function inject()
    word(5)
    word(47); word(s16(c[3])); word(s16(c[4])); word(s16(c[5]))
    word(22); word(s16(c[2]))
    word(21); word(s16(c[1]))
    word(20); word(s16(c[0]))
    word(58)
end

local function dump(tag)
    local ptr = dspace:read_u32(0x0030101)
    log(string.format("%s ptr=0x%08x", tag, ptr))
    for a = BASE, BASE + WORDS - 1, 4 do
        log(string.format("%s %08x %08x", tag, a, dspace:read_u32(a)))
    end
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
            log("probe: sharc=" .. tostring(sharc) .. " dspace=" .. tostring(dspace))
        end
    end
    if not (space and dspace) then return end

    if frame == INJECT - 2 then
        dump("before")
    elseif frame == INJECT then
        inject()
        log(string.format("inject frame=%d c=%d,%d,%d,%d,%d,%d", frame,
            c[0], c[1], c[2], c[3], c[4], c[5]))
    elseif frame == INJECT + 3 then
        dump("after")
        log("complete")
        log_file:close()
        manager.machine:exit()
    end
end)
