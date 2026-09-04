# i960 replacement image

This directory contains the generated Intel i960 host-ROM replacement and its
bounded recovered C units. It is the active firmware target for the C-only
attract milestone; it is not yet a complete game implementation.

Current objective, lifecycle, and checkpoints are defined in the
[reconstruction handbook](../docs/reconstruction.md). Commands shared with the
rest of the project are maintained in [operations.md](../docs/operations.md).

## Build and run

From the repository root:

```sh
./scripts/i960-build.sh
./scripts/run-i960-reconstructed.sh \
  -video none -sound none -oslog -seconds_to_run 1 -skip_gameinfo
```

Capture its startup state with:

```sh
./scripts/trace-i960-reconstructed.sh
```

The build produces separate smoke, reconstructed, clean, and isolated reset
artifacts below `von/build/i960/`. The important outputs are:

- `reconstructed-maincpu.bin`: generated replacement image with approved
  support data;
- `reconstructed-clean-maincpu.bin`: generated code plus only the
  hash-approved original data ranges, with all other bytes filled by `0xff`;
- `reconstructed.lst`: generated-code disassembly with symbols;
- `reconstructed_reset.*`: isolated reset-slice experiment.

Names may evolve; build manifests under `von/build/i960/` are authoritative
for exact paths and hashes.

## Clean-code audit

```sh
./scripts/run-i960-clean.sh \
  -video none -sound none -oslog -seconds_to_run 8 -skip_gameinfo
./scripts/audit-i960-clean-runtime.sh
```

The audit must fail when an observed i960 PC lies outside the generated-code
extent. A provenance pass does not imply behavioral equivalence; the attract
suite owns that result.

## Original disassembly

```sh
./scripts/remote-disasm-i960.sh
```

This generates the original `vonj` listing under `von/build/disasm/`. Static
and runtime findings are retained in:

- [boot-path.md](boot-path.md), the broad address/control-flow notebook;
- [disassembly-annotations.md](disassembly-annotations.md), detailed subsystem
  and routine notes;
- [match-trace-findings.md](match-trace-findings.md), original match geometry
  observations;
- [geometry-transform-fifo-findings.md](geometry-transform-fifo-findings.md),
  bounded response vectors;
- [mame-sharc-precision-upstream.md](mame-sharc-precision-upstream.md), the
  MAME CPU-core precision boundary.

These notebooks contain historical and provisional statements. The ledger,
canonical evidence manifest, and passing verifiers determine promotion.

## Recovered C checks

From `von/`:

```sh
make check-recovered-c
make check
```

The syntax gate compiles recovered translation units independently because
address-specific models may intentionally reuse helper names. Focused tests
live under `von/tools/` and suite membership lives in
`von/tests/manifest.json`.

## Runtime tracing rule

Original `vonj` captures establish evidence. Reconstructed `vonjdev` captures
are comparisons and diagnostics. Do not use reconstructed output to establish
what the original did.

Whole-run PC sets are coverage sieves only. For semantic promotion, capture a
bounded ordered event/state fixture around one hypothesis. The reusable method
and evidence schemas are in
[evidence-and-assets-plan.md](../docs/evidence-and-assets-plan.md).

## Byte reproduction

Byte matching remains a separate research metric because the GCC-based i960
toolchain does not reproduce all original register-link conventions or
instruction choices. Compare an eligible single-range work unit with:

```sh
python3 von/tools/reconstruction_progress.py \
  --compare maincpu/<unit> \
  --original von/build/disasm/vonj-maincpu.bin \
  --generated <generated-slice.bin>
```

Do not add wrappers or stubs solely to improve byte similarity. The pinned
Intel compiler experiment is documented in
[ctools-reproducibility.md](ctools-reproducibility.md).
