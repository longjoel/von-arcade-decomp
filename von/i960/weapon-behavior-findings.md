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

The bout struct is symmetric at `+0x600` (player object `0x503ad0`, mirror
object `0x5040d0`); health occupies `+0x1d8/+0x1d0/+0x1d2`. So the opponent
side is the same offset set plus `0x600`:

| cell | role |
| --- | --- |
| `0x503ca8` | player health snapshot / round max (only written at round transition) |
| `0x503ca0` | player per-frame **working** health (`r4+0x1d0`) |
| `0x503ca2` | player live health **display** (`r4+0x1d2`; eases toward working) |
| `0x50380a` | opponent side (bout-struct promoted `0x503804..0x50381c`); churns, not raw HP |
| `0x5042a8` | opponent snapshot / round max (`0x5040d0+0x1d8`) |
| `0x5042a0` | opponent per-frame **working** health (`0x5040d0+0x1d0`) |
| `0x5042a2` | opponent health **display** (`0x5040d0+0x1d2`) |

Earlier notes mislabelled `0x5042a8` as the "working mirror"; it is the
round-constant snapshot. The opponent working cell is `0x5042a0`, set from
`0x51d1b0` alongside `0x503ca0` at `0x87ce8` and written by the same
`+0x1d0` path. The `0x503ca8 -> 0x503ca2` / `0x5042a8 -> 0x5042a2` copies in
the round-transition routine are why the snapshot pair does not move on a hit.

Re-tabulating the 2026-09-09 replay across all six cells:

```text
cell       drops  rises  big(>200)
w_pl           1      2      2     (round-transition snapshot)
d0_pl         15      2      5
disp_pl      158    100      1     (live per-frame -> use this)
opp          200    205    138     (derived/churn)
w_mir          1      2      2
disp_mir      12    108      2
```

So `0x503ca2` is the live damage signal; it drops in clean per-hit steps while
the opponent-side `0x50380a` mixes hits with round-transition copies. Example
beam drains: `0x5042a2` -8/frame at `f2044..f2047`; `0x503ca2` -9/frame at
`f2326..f2329`.

## Damage signatures observed

From the 2026-09-09 replay, damage lands in two shapes:

- Single hits of 30 / 50 / 70 (discrete projectiles).
- Sustained drains of 8–9 per frame over ~15 frames (beam-style, e.g.
  `f3213..f3229`).

Large jumps (270/357/420/535/738/750) coincide with round-transition display
copies, not hits.

## Open

- Per-weapon damage tensor `[mech][weapon][hit]` and whether any weapon is
  hitscan (damage with no travelling effect). The real damage applier is
  struct-indirect (annotation `0xe4c54 DEMOTED`) and needs a Ghidra backward
  slice or a debugger-PC capture on the working cell.
- Which effect OBA family belongs to which weapon/mech, and missile/mine
  semantics (arming, homing, lifetime, multi-hit).
- A controlled firing oracle: the scripted sandbox never produces accepted
  launches, so per-weapon isolation still needs a real joined input (human
  replay or a validated join path).
