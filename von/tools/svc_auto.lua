-- Closed-loop service-menu entry: polls tile text for the title screen,
-- presses the service button there, then dumps whatever appears.
-- Headless-fast (no video needed): tile RAM is the eyes.
local LOG = os.getenv("VON_SVC_LOG") or "/tmp/svcauto.log"
local SECONDS = tonumber(os.getenv("VON_SVC_SECONDS") or "150")
local log_file = assert(io.open(LOG, "w"))
local function log(msg)
    log_file:write(msg .. "\n")
    log_file:flush()
end

local frame = 0
local space = nil
local fields = {}
local phase = "wait-title"
local hold = 0

local function tiletext()
    local rows = {}
    for row = 0, 63 do
        local chars = {}
        for col = 0, 63 do
            local ok, v = pcall(function()
                return space:read_u16(0x01000000 + row * 128 + col * 2)
            end)
            if ok and (v & 0x8000) ~= 0 then
                local c = v & 0xff
                chars[#chars + 1] = (c >= 0x20 and c < 0x7f)
                    and string.char(c) or "?"
            else
                chars[#chars + 1] = " "
            end
        end
        local s = table.concat(chars):gsub("%s+$", "")
        if s:match("%S") then rows[#rows + 1] = s end
    end
    return rows
end

local function dump(tag)
    local rows = tiletext()
    log(string.format("svc: frame %d %s rows=%d", frame, tag, #rows))
    for _, r in ipairs(rows) do
        if r:match("[A-Z][A-Z]") then log("  |" .. r .. "|") end
    end
end

emu.register_periodic(function()
    frame = frame + 1
    if frame == 1 then
        local cpu = manager.machine.devices[":maincpu"]
        if cpu then space = cpu.spaces[":program"] or cpu.spaces["program"] end
        local port = manager.machine.ioport.ports[":IN0"]
        if port then for n, f in pairs(port.fields) do fields[n] = f end end
    end
    if phase == "wait-title" and frame % 30 == 0 and space then
        for _, r in ipairs(tiletext()) do
            if r:match("INSERT COIN") then
                log(string.format("svc: frame %d TITLE seen", frame))
                if fields["Service 1"] then
                    fields["Service 1"]:set_value(1)
                end
                hold = 10
                phase = "released"
                break
            end
        end
    elseif phase == "released" then
        hold = hold - 1
        if hold <= 0 then
            if fields["Service 1"] then fields["Service 1"]:clear_value() end
            log(string.format("svc: frame %d service released", frame))
            dump("after-service")
            phase = "watch"
            hold = 300
        end
    elseif phase == "watch" then
        hold = hold - 1
        if hold == 150 then dump("watch-mid") end
        if hold <= 0 then
            dump("watch-end")
            phase = "done"
        end
    end
    if frame >= SECONDS * 60 then
        log("svc: session complete")
        manager.machine:exit()
    end
end)
