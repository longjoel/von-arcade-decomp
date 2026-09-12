# Parametric aim: joint-rotation fit (negative result)

> **Working notebook.** Follows `parametric-aim-findings.md`. Tests the
> head/torso/arm aim hypothesis directly from geometry, without decoding the
> SHARC record->matrix composition.

## Method

`/home/longjoel/von-scratch/aim_fit.py` (scratch) parses a geometry capture,
finds the opponent centroid (any non-Temjin mech family present), computes the
opponent direction in the player mech's root frame (`inv(R_root) * d` ->
bearing/elevation), and correlates each canonical Temjin part's parent-relative
local rotation against that bearing/elevation. Part anatomy comes from the
assembled model (`roster_temjin.gltf`): the highest part `009e36c2` is the
head, the root `009e332f` is the upper torso.

## Result (`attract-20260912T`, Temjin vs Dorkas, t=120-150 s, 1200 frames)

- No part tracks the bearing. Best `|r|` is ~0.41 (a leg part vs elevation);
  the head `009e36c2` shows no Y-yaw variation and at most 26 deg of total
  local rotation.
- Local rotation spans are dominated by the limbs (foot/arm joints 84-104 deg),
  i.e. locomotion, not aim.
- The head's local rotation is essentially welded to the torso in this segment.

A cross-check on `human-20260909T021757Z` (Temjin vs Viper2) is also ~0. An
earlier run that suggested `r = -0.98` for the head was a series-alignment bug,
not signal.

## Interpretation

The local joint rotations recovered from the trace do **not** carry the aim.
Either (a) this segment has no lock-on (the fighters are not aiming), or (b) the
aim is applied at the world/SHARC-composition level rather than as a per-joint
local rotation, which is consistent with the parked record->matrix problem.

## Next step if revisited

- Pick a capture with a clear lock-on/melee-approach transition, and gate on the
  kernel's `lock` input, before fitting.
- Alternatively, decode the SHARC composition (parked) so the emitted joint
  angles can be read directly.
