# Geometry recovery and export

## Boundary

```text
i960 object state and packet construction
  -> Model 2 geometry command stream
  -> SHARC affine state and responses
  -> polygon ROM selected by OBA
  -> culling, clipping, depth, texture, and raster output
```

Polygon data and object transforms are separate. OBA selects linked static
polygon records; it does not identify the final per-instance transform.
Runtime matrix state and the SHARC affine tail must be associated through the
ordered command stream.

## Established contracts

- OBA low 22 bits select a four-byte word offset in the assembled polygon ROM.
- Polygon records are linked 40-byte records with triangle/quad, link, and
  depth-selection attributes that must be preserved.
- Object submissions retain OBA, TPA, THA, count, mode, opcode, and order.
- The accepted device matrix is a 3x4 runtime value, not a ROM-resident camera
  or model matrix.
- The SHARC keeps nine affine coefficients plus a three-word translation tail.
- Matrix timestamp proximity alone is insufficient when several writes share
  one timestamp.
- Decoding a polygon does not prove it survived culling, clipping, depth, and
  raster setup.

Address-level support remains in
[disassembly-annotations.md](../i960/disassembly-annotations.md). Retained
runtime observations are in [match-trace-findings.md](../i960/match-trace-findings.md)
and [geometry-transform-fifo-findings.md](../i960/geometry-transform-fifo-findings.md).
The native extraction boundary and provisional rig analyses live in the
separate `von-runner` repository.

## Current asset policy

Assume existing glTF exports and viewer status labels are
`legacy-unreviewed`. Visual identity, stable part count, or a plausible pose is
not enough to promote an asset.

A validated static geometry pack requires:

1. private-ROM audit identity and exact source ranges;
2. deterministic topology/attribute re-extraction;
3. canonical ordered object-submission evidence;
4. sequence-based matrix/object association;
5. payload and intermediate hashes; and
6. transformed-bound, draw-order, and reference render/raster comparison.

Textures, identity, hierarchy, and animation are independent claims. A flat
per-part transform sequence can be validated while a proposed rig remains a
candidate.

## First clean pilot

Use one small stable object, preferably the known arena-floor OBA, rather than
a complete fighter. Recapture it canonically, verify its submission and
transform sequence, deterministically re-extract it, compare it with a
reference frame, and package it with explicit claims. Only then expand to a
fighter assembly.

See [Evidence and assets plan](evidence-and-assets-plan.md) for the pack schema
and `von-viewer` acceptance criteria.

## Stage-2 arena obstacle inventory (manual-02 trace)

Source: `von/build/attract-coverage/manual-02/stage2-geo.log`
(135168 object packets, 196291 matrices, t=139.2-161.3s) and the
`t=150.01` export `stage2-arena.glb` (110 slots, 100 meshes). Local
coordinates equal world coordinates: placing any persistent static
through V^-1 * P against the west-wall matrix returns its local origin
(floor `00800bcb` -> (0,0,0), block `0080078e` -> (0,0,0)).

Persistent arena statics (OBA, local box, submissions in window):

- floor `00800bcb`: x/z +/-320, y -72..0, n=1267 (every frame).
  Matches the movement walls at +/-320 exactly.
- distant ground `0080114a`: +/-2227, n=1267.
- backdrop `0080341b`: +/-2775, y 95..2561, n=1267.
- wall bands N `008020b2` (z -561..-320, y 0..82),
  S `00802937` (z 320..480), E `008022e9` (x 320..480, y 0..104),
  W `00802ed1` (x -543..-320, y 0..136, n=687, every 2nd frame).
- obstacle blocks, 20 tall, 34-58 render tris each:
  `0080078e` x[-156,-124] z[164,236] n=1099;
  `008003dd` x[-156,-124] z[-236,-164] n=993;
  `00800972` x[124,156] z[164,236] n=1219;
  `0080055d` x[124,156] z[-236,-164] n=993;
  `00800126` x[-36,36] z[44,76] and `0080009d` x[-36,36] z[-76,-44]
  (spawn pads: player spawns (0,0,-60), CPU (0,0,60));
  `0080060e` x[204,236] z[-36,36] n=1500 (two instances: arena copy
  plus a far-west duplicate at world (-441,128,-20)).
- far-west set near x=-432: `008006dd` (n=1034, world y -80) plus the
  `0080060e` duplicate. Purpose unknown.

Movement overlay (positions are float bit patterns at 0x00503ad8 /
0x005040d8): blocks show a solid-until-broken pattern that varies per
bout, supporting destructible obstacles. In the audio-queue bout S1,
B1/B2/B3 are approached (15/21/103 margin samples) but never entered
before break frames ~4377/~3910/~6722, then entered freely after
(29/22/81 samples); B4/C are never entered there. The complementary
manual-02 bout shows the mirror image: B1-B3 never entered even with
margin, while the CPU walks through B4 (f=3575-3616) and the `0080060e`
arena copy (f=4333-4360) at ground level with no health change either
side. Either way the blocked region is the full render box plus fighter
radius -- not a simplified shape. Spawn pads are entered from match
start as expected. The recovered box table with per-bout timelines is
`von/i960/recovered_stage_obstacle_boxes.c`.

Tall transient family `00943088`-`00945ed1` (~24 OBAs, 276 verts /
120 tris each, local y-span shrinking 157.8 -> ~131 across the
sequence): one OBA per video frame for ~20 frames, played twice
(t=144.86-145.16 at world (61.5,23.5,137.0), t=156.33-156.63 at
world (76.6,54.0,171.2); placement stable within each burst). TPA
stride is 0x218 (contiguous descriptor array). Not persistent level
geometry; behaves as a transient large effect or collapse sequence.
Identity and trigger are open -- world placements do not coincide
with the walked-through blocks, so it is not their break animation.

Open: collision-code site in i960 still unfound; family trigger needs
input-to-trace time mapping across runs; B1/B2 blocks are unvisited
(solid vs destroyed-unvisited undecided).
