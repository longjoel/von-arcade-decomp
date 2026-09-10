# MCP left-shot probe

Date: 2026-09-09

The custom MAME was launched through `tools/mame-mcp/mame_mcp.py` with the
`core` profile binary. The MCP session saved a paused baseline, continued the
target, and collected MAME output plus the GDB i960 register target. The live
stub reported `i80960kb`, and the new register map exposed 39 usable 32-bit
registers including `pc`, `ip`, and `pip`.

The existing `von/tools/fuzz_battle_ram.lua` was then run through the same MCP
start/save/continue flow with:

- `VON_FUZZ_ONLY=left_shot`
- `VON_FUZZ_BATTLE=2400`
- `VON_FUZZ_HOLD=120`
- `VON_FUZZ_SETTLE=120`
- `VON_FUZZ_TELEMETRY=0x503c08,0x503c0c,0x503c10,0x503c14,...`
- `VON_FUZZ_TAPS=0x503c08,0x503c10`

The held-shot pass changed the player workspace but did not change the
`0x515000` object table. In `0x5039c0`, `0x503c08` moved from `0` to `0x8a00`
over the 120-frame hold, while `0x503c10` moved from `0` to `0x14`.

A six-frame one-frame-pulse pass produced the same object-table result. During
that pass, `0x503c10` increased once per sampled frame (`1, 2, 3, ... 0x14`),
so it is not currently evidence of a per-shot cooldown. The read taps found:

- `0x503c10` read by `0x26524` 20 times, plus the surrounding state readers.
- `0x503c08` read by a different set including `0x343f4` once and
  `0x8d510..0x8d558` during the window.

The twin path was then exercised with two independent MCP-controlled MAME
sessions (GDB ports `23950` and `23951`) and the known-good link preflight.
Both sessions reached the synchronized battle-screen phase and accepted the
left-shot pulses. However, the candidate words were all zero during the
shot windows, the object/transition regions had no launch-like changes, and
the only nearby transition change was the existing screen/state churn. The
read taps saw cabinet-specific state readers, but no evidence that a live
player projectile was created.

Conclusion: the MCP server can now control the custom MAME and coordinate a
linked two-cabinet probe, but this scripted twin flow still does not prove a
human-controlled player. The next valid cadence experiment must begin from a
real joined-player capture (human input or an independently validated join
path), then use the same MCP sequence: save baseline, continue to the target
function, capture the input/state read, and compare projectile/object changes.
Do not add a runner cooldown from the current evidence.

## Gauge-oriented follow-up

The in-fight HUD has three weapon gauges in addition to health. A weapon can
consume the whole gauge or drain it one shot at a time; an empty gauge is
crossed out until it refills. This makes the next probe a state-machine
capture, not just an object-family count:

```text
input edge -> weapon resource change -> accepted launch/effect
                         |                 |
                  empty/crossed       geometry evidence
                         |
                    refill transition
```

The corrected active-low macro replay showed the first left-shot cluster at
frames `2169, 2179, 2186, 2192, 2199, 2208`. The old `0x503bc0` candidate
window stayed non-semantic. A focused write watch over `0x504d00..0x504d7f`
showed that the nearby changes are downstream status rendering: `0x504d28`
and `0x504d30` are written by the status-latch renderers (`0x219d0` and
`0x21a08`), while `0x504d10` is incremented by `0x22670`. These are useful
phase markers but not yet the weapon resource.

Static input-maintenance code at runtime `0x73080` operates on the input
substructure at `g7 = r4 + 0xec`, with byte fields `+0x4c`, `+0x4d`, and
`+0x52..+0x57`. The `+0x52/+0x53` pair has explicit empty/reset logic, but a
shot/no-shot differential replay showed those fields are identical between
the two runs. They are input debounce/repeat timers, not weapon cooldowns.
The recorder's opt-in `VON_WATCH_STRUCT_FIELDS=1` tap remains useful for
finding the actual action/resource structure, but these fields must not be
used as a cooldown implementation.

## Human replay writer probe

The first complete human capture is `human-20260909T022721Z`. Its macro has
left-shot rising edges at frames `2169, 2179, 2186, 2192, 2199, 2208`, with
intervals `10, 7, 6, 7, 9`; this establishes a six-frame minimum between those
human input edges, not yet a six-frame accepted-launch cadence.

The macro was replayed through MCP with the capture's original configuration
and NVRAM. A write-watch over `0x503bbc`, `0x503c08`, `0x503c10`, and
`0x503cb8` was armed successfully. The active main-CPU writer PCs included
`0x24fdc..0x24ff8`, `0x25004`, `0x2505c`, `0x252a4`, `0x25330`,
`0x26404`, `0x26428`, `0x264fc`, `0x26544`, `0x265a8`, `0x26654`, and
`0x266a8`. Earlier writer summaries were genuinely empty; the later writers
are regular per-frame input/state maintenance, so they do not identify launch
acceptance by themselves.

The recorder now supports bounded `VON_WATCH_LOG_WRITES=1` logging with
`VON_WATCH_LOG_FROM`/`VON_WATCH_LOG_TO`. The next probe should use that log
around a replay that is visually/state-validated as the same joined bout,
then correlate a non-maintenance write or geometry birth to each shot edge.

## Deterministic geometry probe

The combined `mcp-geometry` build was then run through the MCP server with a
selection/start sequence and a left-shot pulse every six emulated frames from
frame 2400 onward. The geometry trace contains the expected player family
`0081` continuously, but contains no `0089` or `008a` objects during the shot
window. This run therefore still does not demonstrate an accepted projectile
launch.

Family `00bb` does appear in short bursts near individual pulse times, but
`von/oba_registry.json` classifies it as an effect family, not ordnance. Those
bursts are secondary evidence only and must not be treated as shot cadence. The
accepted-launch cadence remains unresolved.

The recorder now has `VON_RECORD_BOOTSTRAP=1`, which drives the known
coin/two-right/start sequence before a preserved-timing macro. A bootstrap
replay confirmed the sequence itself (`f900`, `f1125`, `f1170`, `f1590`) and
produced the same active input-maintenance writers, but its workspace and
object-table evidence still showed no `0089`/`008a` ordnance. The bootstrap is
therefore a reproducibility aid, not yet a valid launch oracle.

## Current gauge boundary

The enclosing player object is recoverable in live code: with `g7=0x503bbc`,
`r4=0x503ad0`. The previously suspected object fields `r4+0x170`,
`r4+0x172`, and `r4+0x184` are action/transition and movement state; their
shot/no-shot values did not provide a three-gauge signature. A broad write
watch over `0x504d00..0x504e00` also showed regular status initialization and
renderer updates, but was too expensive and was stopped before producing a
validated launch correlation.

Therefore the first defensible gauge goal is narrower: capture one real
joined-player bout with the HUD visible, identify one accepted left-shot
edge, and record the first three-value resource transition (decrement,
zero/crossed state, refill) before generalizing to the other two weapons.

The replay control itself is now verified. With preserved macro timing,
shot-on frames apply logical mask bit 0 and read `:IN1` as `0x0ffe`; the
matched shot-off run reads `0x0fff`. This rules out the earlier possibility
that active-low replay polarity was hiding the control. However, the two
replays still produce identical geometry and the same non-launch object
timeline. The input-maintenance routine at `0x73080..0x733f4` consumes the
input structure at `0x503bbc`/`r4=0x503ad0`, but no accepted weapon launch is
visible in this attract/non-bout replay. The next experiment must load or
capture a true joined-fight state before using geometry or resource writes as
launch evidence.

## Authoritative checkpoint probe

The custom `mcp-geometry` binary now accepts `VON_MCP_ALLOW_STATE_LOAD=1` for
an opt-in load while anonymous Lua/autoboot timers are pending. The recorder
can schedule `VON_RECORD_LOAD_STATE=joined3000` from frame 2, and its post-load
notifier re-arms macro playback and invalidates cached input-field handles.
This avoids comparing boot-state replays: the loaded run restores screen hash
`20bf1d00` and the saved fight-state window beginning at frame 3.

Replaying `macro.txt` with offset 3000 reproduces the first human left-shot
edge at local frame 731 (capture frame 3731); the active-low `:IN1` read is
observed as `0x0ffe`. The paired no-input control and the current broad
`0x5039c0`/`0x504d80` windows remain identical, so those windows are not the
weapon gauges. The next probe should use this checkpoint pair to watch the
HUD/resource storage or its writer routine around the accepted edge.

## Candidate rejection: `0x504dac` / `0x504db0`

The longer human capture (`human-20260909T021757Z`) made it possible to
check the two fields that superficially resemble a shot timer. `0x504dac`
does change around several left-shot edges, and `0x504db0` supplies small
period-like values (`5`, `10`, `30`). They are not the three weapon gauges:
the pair also resets repeatedly while no left-shot edge is present.

The static path explains that behavior. The status/animation routine at
`0x74d20` reads `0x504dac` as a bitfield and derives a mode mask, then writes
`0x504db0`; the helper at `0x73498` updates the pair as a quad. The pair is
therefore a selected status/animation mode, not a resource array. This is a
useful MCP elimination because it prevents the apparent six-frame rhythm
from becoming a false cooldown implementation.

The remaining target is the player object reached through the live input
context (`g7=0x503bbc`, `r4=0x503ad0`). The next MCP run should log a compact
field window for that object across one accepted edge, one rejected tap, and
the first refill. A valid gauge candidate must show three independent values,
decrement on accepted shots, and return toward its starting value without
being driven by input-repeat maintenance.

## Player cooldown boundary

The adjacent bytes `r4+0x138..0x13a` (`0x503c08..0x503c0a`) are a false
candidate. They alias the input structure at `g7+0x4c..0x4e`; the live write
tap sees the input-maintenance routine at `0x7302c` decrementing them and
`0x73170`/related paths resetting them to `0xff`. Their rapid transitions are
input-repeat state, not weapon gauges.

The actual three cooldown timers are 16-bit fields in the same player object:

| slot | object field | live address | availability |
| --- | --- | --- | --- |
| 1 | `r4+0x1ec` | `0x503cbc` | `r4+0x1de` / `0x503cae` |
| 2 / left shot | `r4+0x1ea` | `0x503cba` | `r4+0x1dd` / `0x503cad` |
| 3 / combined shot | `r4+0x1ee` | `0x503cbe` | `r4+0x1df` / `0x503caf` |

The timer service at `0x4a430..0x4a598` decrements all three fields once per
frame, compares them with the weapon-specific thresholds, and writes the three
availability bytes. This directly explains the HUD's refill and crossed-out
state.

## Recovered left-shot cadence

The one-frame analyzer now reads the true 16-bit timers rather than the input
counters. In the authoritative human capture
`human-20260909T021757Z`, slot 2 starts its cooldown at frames `2175`, `2685`,
`3875`, `4530`, `4935`, `5670`, and `6300`; the normal active durations are
`300` frames each. The availability byte `0x503cad` reads `0` for the first
~20 frames of each window (see the correction section at the end of this
file). The independent capture
`human-20260909T022721Z` repeats `300`-frame windows at `2205`, `2760`,
`3775`, `5065`, and `5400`. The two observed `600`-frame runs are stacked or
extended cooldown activity, not a different base tick.

Therefore the recovered normal left-shot cooldown is **300 emulated frames**
(approximately 5 seconds at 60 Hz). Left-shot edges during that unavailable
window are rejected; the edge-to-timer-start delay varies with the attack path
(6–29 frames in the first capture's clear examples and 6–47 in the second),
so the input edge itself is not the cooldown boundary. The earlier 8–23-frame
“rapid-fire cadence” was caused by correlating input counters and animation
state, and is superseded by the 16-bit timer evidence.

The MCP bootstrap replay independently validated the mechanism at one-frame
resolution, though its different starting state uses a 240-frame slot-2
window. That replay's timer runs were exactly `240, 240, 240...`; the real
human bouts consistently use `300`. The reusable analyzer is in
`tools/analyze-shot-cooldown` and reports both the timer starts and exact
zero-crossing durations.

The third weapon is selected by holding both weapon inputs simultaneously; it
is not a separate button. Future probes should therefore distinguish three
input classes: left only, right only, and left+right together. The combined
class should correlate with slot 3 (`0x503cbe`, availability `0x503caf`).

## Reusable three-input probe

`von/tools/sandbox_versus.lua` now accepts `VON_SANDBOX_WEAPON_CASE=left`,
`right`, or `both`. Each run drives only that input class during the battle
shot phase and, with `VON_SANDBOX_WEAPON_LOG=1`, records the three 16-bit
timers and availability bytes on every pulse:

```text
VON_SANDBOX_WEAPON_CASE=both VON_SANDBOX_WEAPON_LOG=1 \
  ... -autoboot_script von/tools/sandbox_versus.lua
```

Use the MCP state-load flow to restore the same battle baseline before each
case. Summarize a captured log with `tools/analyze-weapon-probe`; it reports
timer starts, zero-crossing durations, and availability transitions per slot.

## Automated-flow notes

The MCP sandbox required two corrections before it became useful: field
activation must honor the cabinet's active-low `defvalue`, and the timer write
veto must be disabled. With those settings, the custom instrumented MAME runs
a real 1P bout and the bootstrap/macro probe records the 16-bit cooldowns at
one-frame resolution. Leaving the timer veto enabled can trigger an i960
`Unhandled 00` followed by debugger teardown failure; that is a probe-tap
interaction, not part of the recovered game cadence. The active-level option is
kept opt-in so existing sandbox runs are not silently changed.

## Availability-byte correction (review 2026-09-10)

The earlier claim that `0x503cad` "is clear for the same 300-frame windows"
is wrong. Re-tabulating both human captures at 5-frame state sampling shows
bit0 of each slot byte (`0x503cad`, `0x503cae`, `0x503caf`) reads `0`
only while that slot's timer reads >= ~281, i.e. the first ~20 frames of a
cooldown, then returns to `1` while the timer keeps counting down:

```text
f2170->2175: bit 1->0, timer 0->299      (fire sets the timer)
f2190->2195: bit 0->1, timer 284->279    (clears as the timer crosses ~280)
```

Every 0->1 flip in both captures lands on a timer reading of 276..285, and
the 1->0 flips always coincide with a fresh timer start. Slot 1's timer never
exceeds ~22, so `0x503cae` never reads `0` in-fight — consistent with a
rapid-fire weapon class that never trips the gate. Pre-fight the bytes read
`0` until the service arms (frame 1630 / 1775). So bit0 is a "freshly fired"
flag, not a 300-frame availability state; the 300-frame gate itself lives in
the 16-bit timer, which the launch selector must be reading directly.

The 1->0 flips also reveal stacking: re-firing mid-cooldown ADDS ~295 to the
running timer (`200->495` at f5040, `53->348` at f4025 in the second
capture), which explains the 600-frame runs without a second base tick.

Bit1 of these bytes is still unresolved. It appears in 10-85 frame episodes
on `ae`/`af` (once on `ad`), almost always riding on bit0=`1`, and one
episode ends exactly when another slot fires (`af` 3->1 at f3895 as slot 2
starts). It is not held input (no shot bits in the macro during the
3810-3895 episode) and not timer-driven (slot 3's timer never runs). The
`VON_SANDBOX_WEAPON_WRITES=1` tap covers `0x503c08..0x503c0b` and can supply
the writer PCs for these transitions in a future run.
