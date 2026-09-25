-- Compose the SCSP voice probe with the scripted gameplay sandbox.
--
-- Loads the read-only `trace_scsp_voices.lua` write taps first, then runs the
-- sandbox autoinput so the bout actually triggers sound commands and SCSP
-- key-ons. Both scripts register their own periodic callbacks.
--
-- Environment: VON_VOICE_PROBE, VON_SANDBOX_BASE (script paths)

local probe = os.getenv("VON_VOICE_PROBE") or "/src/von/tools/trace_scsp_voices.lua"
local base = os.getenv("VON_SANDBOX_BASE") or "/src/von/tools/sandbox_versus.lua"
dofile(probe)
dofile(base)
