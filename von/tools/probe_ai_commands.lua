-- Per-object opponent-AI command tap.
--
-- `probe_ai_state.lua` samples the shared AI globals every frame, so the
-- class -> command pairing is noisy (0x504d94/0x504d68 are last-writer for
-- both objects and the command persists). This probe taps the write to the CPU
-- object's command word (object+0x108) and reads the behaviour class *at the
-- instant of the write*, giving a clean class -> command map to validate the
-- Godot AI port (scripts/von_ai.gd).
--
-- Must run under the interpreter (`-nodrc`): i960 DRC-compiled writes bypass Lua
-- data taps, so the tap never fires otherwise.
--
--   VON_AICMD_LOG=out.log VON_AICMD_SECONDS=45 ./bin/vonctl run -nodrc -video none \
--     -autoboot_script von/tools/probe_ai_commands.lua

local SECONDS = tonumber(os.getenv("VON_AICMD_SECONDS") or "45")
local LOG_PATH = os.getenv("VON_AICMD_LOG") or "von-ai-commands.log"

local CPU = 0x005040d0
local CMD = CPU + 0x108        -- 0x005041d8, the synthesised command word
local G_CLASS = 0x00504d94
local G_SECTOR = 0x00504d68
local G_MA = 0x00504dac
local G_MB = 0x00504db0

local file = assert(io.open(LOG_PATH, "w"))
local frame = 0
local space

local function setup()
    local cpu = manager.machine.devices[":maincpu"]
    if not cpu then return false end
    space = cpu.spaces[":program"] or cpu.spaces["program"]
    if not space then return false end
    space:install_write_tap(CMD, CMD + 3, "von-cpu-command",
        function(offset, data, mask)
            local class, sector, ma, mb = 0, 0, 0, 0
            pcall(function()
                class = space:read_u16(G_CLASS)
                sector = space:read_u16(G_SECTOR)
                ma = space:read_u16(G_MA) & 0xff
                mb = space:read_u16(G_MB) & 0xff
            end)
            file:write(string.format(
                "frame=%d cmd=%04x class=%d sector=%d ma=%02x mb=%02x\n",
                frame, data & 0xffff, class, sector, ma, mb))
            return data
        end)
    return true
end

emu.register_periodic(function()
    frame = frame + 1
    if not space then
        if frame % 60 == 1 then setup() end
        return
    end
    if frame % 60 == 0 then file:flush() end
    if frame >= SECONDS * 60 then
        file:flush()
        manager.machine:exit()
    end
end)
