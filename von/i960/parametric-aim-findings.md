# Parametric aim: what a series of SHARC opcode calls does

> **Working notebook.** `KNOWN` = verified from trace/listing; `LIKELY` =
> consistent multi-source reading; `SPECULATIVE` = unconfirmed hypothesis.

This extends [motion-emitter-findings.md](motion-emitter-findings.md). The
earlier note decoded one opcode *program* (a per-part transform). Here we ask
what a whole *series* does across the game, and test the hypothesis that the
head/torso/arms are aimed parametrically at the opponent.

## Method: trace every FIFO writer

Patch `0049` was broadened from a fixed PC window to **every write** to the
copro FIFO at `0x884000`, anchored at `model2b_state::copro_fifo_w` (the twin
`model2c` is not used by `vonj`). Env knobs: `VON_FIFO_T0/T1`,
`VON_FIFO_PC_MIN/PC_MAX`, `VON_FIFO_MAX`. Rebuild on `drone0` with
`VON_MAME_PATCH_SET=select-sweep`; capture attract with `-log -oslog`.

A ~19 s attract window yields **1,295,487 writes** from **1,231 distinct i960
PCs**. The old PC filter hid almost all of them.

Tooling: `von/tools/decode_fifo_program.py` groups the stream into packets
(transform and sequencer grammars, CSV export);
`von/tools/scan_fifo_programs.py` enumerates per-PC roles and the opcode
vocabulary.

## Programs seen

| program | where | form |
| --- | --- | --- |
| part transform (`KNOWN`) | `0x8d400`/`0x8d5d0`/`0x8dd40`/`0x8e120` emitted from `0x8d488`/`0x8d714`/`0x8de14`/`0x8e164` | `05 2f <off0..2> 16 <rotA> 15 <rotB> 14 <rotC> 3a <read> [06]` |
| look-at (`KNOWN`) | i960 `0x9ed44` | `25 <x> <y> <z>` — SHARC **angular projection**, 3 floats in, 2 angles out (~737 calls) |
| spherical (`KNOWN`) | i960 `0x9ee58` | `45 <a> <b> <c>` — SHARC **spherical projection** (~1002 calls) |
| frame sequencer (`KNOWN` shape) | i960 `0x93560`, `0x40e38` | `05 12 <g0 g1 g2> 15 <g3> 13 <e f g> [06]` with a modulo-120/168 counter |

The emit-side opcode vocabulary is essentially the **full 78-entry table**, not
just the transform handful: `0x14/15/16` (rotations), `0x1f` (distance),
`0x1d/1e` (cos/sin), `0x25` (angular), `0x35` (stateful div), `0x41`
(byte-lane), `0x45` (spherical), `0x47` (geometry predicate), `0x49` (3D
distance), and more.

## What the aim programs do (`KNOWN` inputs, `LIKELY` role)

The `0x9ed44` program, once per update per target, writes
`25` then three big-endian floats. Sample `(x,y,z) = (563.3, 18.0, -141.0)`,
magnitude ~580, changing every frame; `r6` is a target index (`0x0a`/`0x0b`),
`g2` a destination in the `0x00565xxx` pose/aim workspace. The SHARC returns
two angles. That is a **look-at**: target vector in, yaw/pitch out.

The `0x9ee58` program writes `45` plus `0`, a fixed-point angle (`0x2baa`,
`0x2e5d` per target) and a slowly ramping float — the inverse operation,
rebuilding a direction from spherical components.

Destination `0x00565xxx` sits beside the six per-mech pose slots around
`0x562430` from the motion-emitter note, consistent with aim angles being
folded into the pose used by the transform emitter.

## Does it track the opponent? (`LIKELY`, not conclusive)

Correlating the `0x25` look-at azimuth against the opponent direction derived
from the geometry trace (mech centroids) gives, for the strongest pairs,
**r ≈ 0.8** (e.g. Temjin `9e` -> `a9`/`ab`). That supports the aim hypothesis.
But the match is noisy: geometry translations are camera-relative while the
look-at vector is in the game's world space, and the family labels are
ambiguous.

Correlating the look-at azimuth directly against the **emitted body-part**
rotations (`0x8e164` slots) is weak (max `r ≈ 0.34`), so the head/torso are
**not** among the body-emitter slots measured. The aiming joints are driven
elsewhere (a different emitter or the pose-slot consumer).

## Status and next steps

- Parametric aim is **structurally confirmed**: the game computes a
  target-relative vector and calls the SHARC angular/spherical projection
  opcodes continuously.
- The head/torso/arm **binding** is still open. Next:
  1. find which emitter consumes the `0x00565xxx`/pose-slot angles (correlate
     slot values with the `0x25` output, not just the input vector);
  2. recover the i960 routine around `0x9ed44`/`0x9ee58` as annotated C and
     identify where the target vector comes from;
  3. capture a lock-on transition (melee approach) and watch the aim angles
     converge, to tie the geometry bearing to a specific bone.
