# Twin-stick input map (empirical, versus sandbox)

> `observed:<sandbox-sweep>`; measured from the versus harness, not integrated.

## Port layout (`model2.cpp`, `INPUT_PORTS_START(von)`)

Both sticks are per-direction bits, all `IP_ACTIVE_LOW`:

| byte | bits |
| --- | --- |
| `IN1` (P1 left stick + left buttons) | `0x01` L-SHOT, `0x02` L-DASH, `0x10` L-DOWN, `0x20` L-UP, `0x40` L-RIGHT, `0x80` L-LEFT |
| `IN2` (P1 right stick + right buttons) | `0x01` R-SHOT, `0x02` R-DASH, `0x10` R-DOWN, `0x20` R-UP, `0x40` R-RIGHT, `0x80` R-LEFT |

**MAME Lua `ioport_field:set_value()` is logical** (1 = pressed); it already
applies the field's active level. The sandbox's optional `ACTIVE_LEVELS=1`
"honour the electrical level" path is therefore an inversion bug — it disables
the sticks and turns 1-of-N shot pulses into held shots. Use `ACTIVE_LEVELS=0`.

## Method

`scripts/capture-bout.sh` + `von/tools/sandbox_versus.lua`
(`VON_SANDBOX_PROGRAM=probe`) drives one held P1 action set for
`VON_SANDBOX_PROBE_FRAMES` from battle start and records per-frame P1 pose.
`scripts/sweep-sticks.sh` runs the grid in parallel. Start state `(0,-60)`,
facing +Z (toward the opponent); +X is the mech's right on the ground plane.

## Recovered mapping (120-frame holds)

| hold | dx | dz | dyaw | reading |
| --- | --- | --- | --- | --- |
| `up,up2` | 0 | **+193** | −7 | both forward → walk forward |
| `down,down2` | 0 | **−181** | −6 | both back → walk back |
| `left,left2` | **−139** | 0 | −171 | both left → strafe left |
| `right,right2` | **+171** | 0 | +182 | both right → strafe right |
| `right,left2` | 0 | 0 | 0 | pushed together → **guard** |
| `left,right2` | 0 | 0 | −21 | pulled apart → **jump** |
| `up,up2,dash` | 0 | **+356** | −7 | forward dash |
| `right,right2,dash` | **+318** | +13 | +331 | right dash |
| `dash` / `shot` / `right_shot` alone | 0 | 0 | ~0 | no-ops alone |
| `up` / `up2` / `left` / `right` alone | ~½ | ~½ | large | single stick → translate + turn |

The translation is the **sum** of the two sticks and the twist is their
**difference**; sticks together = guard, apart = jump. This is exactly the
`VonInputReader.from_sticks` derivation in `von-godot`.

## Open items

- **Magnitudes.** Single-stick holds translate ~½ of the two-stick holds, but a
  single stick **plus dash** reaches the full dash distance (~318 ≈ the recovered
  4.2 u/f × 69f). So dash uses full stick deflection while walk combines both
  sticks; the walk/dash magnitude normalization still needs fitting.
- **Wall-contact fault.** A sustained hold that pins P1 against the ±320 arena
  wall trips a MAME i960 fault (`Unhandled ff`/`00`); keep probe holds short.
- `dyaw` on strafe mixes the player's passive auto-face (the mech keeps facing
  the opponent) with stick twist; separate them before fitting turn rates.
