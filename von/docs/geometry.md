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
