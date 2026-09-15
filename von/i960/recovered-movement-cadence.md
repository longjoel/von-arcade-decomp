# Recovered horizontal movement (cadence)

> `observed:<ram-telemetry>`; probed with `von/tools/probe_move_cadence.lua`
> (player x/z = object+0x08/+0x10), not integrated.

## Method

Hold both sticks a direction from rest and release, logging per-frame position.
Player starts at (0, -60) facing +Z; short holds keep off the +-320 walls.

## Profile (per-frame path length, u/f)

**Forward** (both sticks up, 60 frames):

```text
0 -> 2.02 over 11 frames   (~0.18 u/f^2 launch, near-linear)
2.02 -> 1.75 by ~f9618     (short settle)
1.75 -> 1.55 by ~f9667     (slow decay,~-0.004/frame)
... then a slow rise toward ~2.9  (long hold; previous run reached 2.89)
```

**Back** (both sticks down, 60 frames): `0 -> 1.74` over 11 frames, a short
bump to ~1.9, a sharp drop to **1.13** at f9818, then a slow rise to ~1.52.

**Strafe** (both sticks right): `0 -> 1.87` over 12 frames, drop to 1.46, slow
rise to ~1.69. Strafe/forward steady ratio is ~0.58.

**Release:** the mech stops within ~**1 frame** (f9660 released -> f9662 d=0);
there is **no deceleration coast**. Back-release likewise.

## What this means

- **No coast.** The earlier kernel eased velocity down at `RV_ACCEL` (took ~13
  frames to stop from the cap). The kernel now snaps horizontal velocity to zero
  when the stick returns to centre.
- **Launch accel ~0.18 u/f^2** for ~11 frames matches the kernel's `RV_ACCEL`
  (0.16). The steady cap is direction-dependent (forward ~1.55 rising to ~2.9,
  back ~1.13-1.52, strafe ~0.58 of forward).
- The **non-monotonic** shape (fast launch, settle, slow decay, slow rise) is
  not a first-order ramp; it is consistent with animation root motion layered on
  the simulation velocity. Not yet modelled.

## Open

- Fit the exact curve (candidate: two time constants, or an animation root-motion
  term) so the launch/settle/cruise shape can be reproduced rather than the
  current constant-accel ramp.
- Direction-change decel (forward -> strafe/back) and the turn-while-walking
  cadence were not measured.
