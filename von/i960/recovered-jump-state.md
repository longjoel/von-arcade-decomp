# Recovered jump state

> `observed:<ram-telemetry>`; probed with `von/tools/probe_jump_state.lua`
> (player object `0x503ad0`), not integrated.

## Cells

Found by differencing the player object across a jump
(`von/tools/probe_player_dump.lua`):

| cell | object offset | meaning |
| --- | --- | --- |
| `0x503ad8` | `+0x08` | x (float) |
| `0x503adc` | `+0x0c` | y (float) |
| `0x503ae0` | `+0x10` | z (float) |
| `0x503c20` | `+0x150` | vertical velocity (float) |
| `0x503c28` | `+0x158` | body heading / rotation (swings through a jump) |
| `0x503b70` | `+0xa0` | aim-tracking gate (parametric-aim-findings.md) |
| `0x503ca0` | `+0x1d0` | working health |

The old note that position lives at `0x503ad8/0x503adc/0x503ae0` is off by the
object base: those are `object+0x08/+0x0c/+0x10`.

## Jump arc (exact)

Trigger: outward twin-stick flick, left stick LEFT (`IN1 0x80`) + right stick
RIGHT (`IN2 0x40`) together (recovered-twin-stick-map.md). One clean jump
(`probe_jump_state`, flick f9600-9610):

```text
takeoff vy = 1.755      (first sample 1.800 after the pre-integrate gravity)
gravity    = -0.030 / frame^2
apex        = 53.10 at f9664 (64 frames after takeoff)
land       ~ f9721          (flight ~115 frames)
```

This exactly matches `recovered_player_physics.c` (apex 53.07, ~117-frame
flight).

## The jump commits until landing

While airborne, none of these changed y/vy or set `object+0x174` (the action):

- **left dash** (f10635-10655, mid-ascent, and f10600s)
- **left shot** (f10940-10960, at the apex)
- **repeat jump chord** (f9650-9660 mid-ascent; f9952-9962 ~apex)

So the mech has one ballistic option per airborne frame: it flies the arc it
was launched with. That matches the arcade feel that you either let the jump
run to the peak or commit to it; mid-air dash/attack/re-jump are ignored.

## Tracking / lock is not apex-gated

The aim-tracking gate `object+0xa0` (see `parametric-aim-findings.md`) is
**cleared at takeoff** and **re-engages during the ascent** (y ~= 13, ~6 frames
in), then generally stays on through apex and descent. In one release-jump it
toggled off near the apex (y ~= 44) and back on later, consistent with the gate
tracking whether the opponent is inside the aim arc rather than a fixed
"lock at the peak".

So the probe does **not** support "you lock on at the peak": the aim gate turns
on *before* the apex. It also does not contradict it for a *different* signal
(the turret aim angles or the body auto-face), which were not measured here.

## Open

- **Turret aim vs bearing across a jump.** Log the head/torso aim angles (the
  `0x00565xxx` pose slots fed by the SHARC look-at, `parametric-aim-findings.md`)
  and the opponent bearing through a jump against a CPU opponent, to test
  whether the aim converges only at the apex. The synthetic 2P start has an
  idle P2, which may not exercise the same lock behavior.
- **Body heading (`+0x158`) during a jump** swings wildly (the mech flips), so
  it can not be read as a plain yaw; the clean heading may only be valid on the
  ground.
- **Hover / hold chord.** Holding the flick through apex+landing did not produce
  a hover in this probe (a normal arc); the previously noted hover (holding
  apex ~50 frames) needs a different input or state.
