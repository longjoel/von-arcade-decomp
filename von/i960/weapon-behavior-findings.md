# Weapon behavior and damage findings

Working notes for rebuilding Virtual-On weapon behavior. Complements
`mcp-left-shot-probe.md` (cooldowns) and `docs/combat.md` (in-kernel model).

## What is already recovered

### Weapon selection and cooldowns (from `mcp-left-shot-probe.md`)

The third weapon is not a separate button: it is left+right held together.
The three 16-bit cooldown/gauge timers live in the player object
(`r4 = 0x503ad0`, `g7 = 0x503bbc`):

| slot | input | timer | availability | recovered duration |
| --- | --- | --- | --- | --- |
| 1 | right shot | `0x503cbc` (`r4+0x1ec`) | `0x503cae` | rapid fire (never exceeds ~22–40) |
| 2 | left shot | `0x503cba` (`r4+0x1ea`) | `0x503cad` | 300 frames |
| 3 | left+right | `0x503cbe` (`r4+0x1ee`) | `0x503caf` | combined |

Service at `0x4a430..0x4a598` (and a second family at `0x646c0..0x64810`)
decrements all three once per frame and writes availability. Re-firing during
a cooldown stacks (~+295 in the human captures).

Observed in the 2026-09-09 human replay (`replay-weapons/record.log`):
slot-2 starts at `f3041, f5658, f5840, f5933, f7494`; slot-1 starts at
`f2215, f2336, f2381, f2426, f2608, f2934, f3144, f5538, f6365, f6545, f7350`.

### Effect geometry classification

`von/tools/classify_weapon_effects.py` splits each OBA's appearances into
contiguous spawn runs and classifies them. On `attract-20260912T` it finds
four behavior buckets (non-stage, non-mech families):

| family | lifetime | peak speed | displacement | class |
| --- | --- | --- | --- | --- |
| `0098xxxx` (OBA stream) | 4–5 f | ~29 u/f | ~46 u | fast shot / beam segment |
| `0099d57b` | 36–177 f | ~58 u/f | up to 827 u | fast projectile / missile |
| `00a3xxxx` | ~155 f | ~8 u/f | ~335 u | slow homing missile |
| `009237e5` | 97 f | ~59 u/f | 638 u | projectile |

It reported 257 projectile runs vs 226 linger / 227 static / 256 drift runs in
the attract capture. `00bb` is an effect family (muzzle/impact), not ordnance.

## Health cells (from `disassembly-annotations.md`)

| cell | role |
| --- | --- |
| `0x503ca8` | player **working** health |
| `0x503ca2` | player health **display** (copied at round transition, `0xe4c54`) |
| `0x50380a` | opponent side (bout-struct promoted fields `0x503804..0x50381c`) |
| `0x5042a8` -> `0x5042a2` | working -> display mirror pair |

Use the working cells for damage; the display cells only update at round
transitions, so they read equal to each other during a bout.

## Replay harness

`von/tools/record_human_session.lua` replays a captured macro from boot and,
with `VON_RECORD_WEAPON_LOG=1`, now logs each frame:

```text
weapon: f<frame> resources=<b0,b1,b2> availability=<b0,b1,b2> timers=<t1,t2,t3> hp=<p,opp,beam,beammirror>
```

The 2026-09-09 human macro replays cleanly from boot (fresh NVRAM) and
reproduces the slot-2 starts within 5 frames. `sandbox_versus.lua` was also
extended to log health, but its scripted P1 does not produce accepted launches
(availability stays `01,01,03`), so it is not a damage oracle.

## Damage signatures observed

From the 2026-09-09 replay, damage lands in two shapes:

- Single hits of 30 / 50 / 70 (discrete projectiles).
- Sustained drains of 9 per frame for ~17 frames (beam-style, e.g.
  `f3213..f3229`), sometimes 6 per frame.

Large jumps (270/357/420/535/738/750) coincide with round-transition display
copies, not hits.

## Open

- Per-weapon damage tensor `[mech][weapon][hit]` and whether any weapon is
  hitscan (damage with no travelling effect).
- Which effect OBA family belongs to which weapon/mech, and missile/mine
  semantics (arming, homing, lifetime, multi-hit).
- Disambiguate the opponent working-health cell from the player display cell.
