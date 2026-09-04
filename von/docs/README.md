# Documentation map

This directory is the canonical entry point for project documentation. Current
workflow and policy live here; generated reports and low-level research
notebooks remain at their established paths.

## Start here

| Document | Purpose |
| --- | --- |
| [Reconstruction](reconstruction.md) | Active objective, scope, lifecycle, checkpoints, and work-unit routine. |
| [Evidence and assets plan](evidence-and-assets-plan.md) | Trace methodology, cleanup, evidence packs, and the `von-viewer` showcase plan. |
| [Operations](operations.md) | Build, run, trace, test, and deployment commands. |
| [Geometry](geometry.md) | Current geometry/export boundary and validation status. |
| [Audio](audio.md) | SCSP captures, sample extraction, reconstruction status, and validation tiers. |
| [SHARC](sharc.md) | Stable recovered contracts, freeze rule, and MAME precision boundary. |

## Generated truth

These files are generated from machine-readable inputs and must not be copied
into narrative documents:

- [Current reconstruction status](../generated-status.md)
- [Attract integration worklist](../attract_worklist.md)
- `von/reconstruction_ledger.json`
- `von/evidence/manifest.json`
- `von/tests/manifest.json`

Run `./scripts/status.sh` for live values. The checked-in Markdown is current
only when regeneration produces no diff.

## Hardware and subsystem references

- [Board and ROM chip map](../chip-map.md)
- [ROM inventory snapshot](../phase0-inventory.md)
- [Versus/link findings](../versus-link-findings.md)
- [Communication Z80 notes](../cpu3-disassembly.md)
- [Ghidra workflow](../ghidra/README.md)
- [i960 build and runtime guide](../i960/README.md)
- [Intel CTOOLS reproducibility](../i960/ctools-reproducibility.md)

## Low-level evidence notebooks

The following are address-level working notebooks. They preserve useful static
and runtime observations, but their prose is not automatically canonical. A
claim becomes current only when consumed by a registered verifier or promoted
through the lifecycle in [Reconstruction](reconstruction.md).

- [i960 boot-path notebook](../i960/boot-path.md)
- [i960 disassembly annotations](../i960/disassembly-annotations.md)
- [Match trace findings](../i960/match-trace-findings.md)
- [Geometry FIFO fixture notes](../i960/geometry-transform-fifo-findings.md)
- [MAME SHARC precision investigation](../i960/mame-sharc-precision-upstream.md)

## Documentation rules

1. Put current policy and workflow in `von/docs/`.
2. Put address-level findings beside the relevant firmware under `von/i960/`.
3. Put commands in `operations.md`, not in multiple overview files.
4. Generate status and queue reports; do not maintain totals by hand.
5. Mark historical snapshots and provisional interpretations explicitly.
6. Prefer links to canonical evidence IDs over links to mutable raw captures.
7. When a notebook becomes obsolete, retain its Git history rather than a
   second competing "current" document.
