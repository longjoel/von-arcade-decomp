# i960 Host ROM Prototype

This directory contains the first native i960 build target for the Virtual-On
host ROM replacement. It is intentionally a hardware smoke test, not a game
implementation.

Build it from the project root:

```sh
./scripts/i960-build.sh
```

The build preserves the original smoke-test image and also produces a
separate C reconstruction image. Run the latter with:

```sh
./scripts/run-i960-reconstructed.sh -video none -sound none -oslog -seconds_to_run 1 -skip_gameinfo
```

Capture its early startup trace with `./scripts/trace-i960-reconstructed.sh`.

For the code-isolation test, build and run the clean image:

```sh
./scripts/i960-build.sh
./scripts/run-i960-clean.sh -video none -sound none -oslog -seconds_to_run 8 -skip_gameinfo
```

`reconstructed-clean-maincpu.bin` contains only generated C/assembly startup
code and the hash-verified asset ranges declared in
`approved_data_ranges.json`; all remaining ROM space is filled with `0xff`.
Its generated manifest records every copied range and output hash. This image
currently completes recovered hardware initialization and then stays in the
heartbeat loop; the attract scheduler is the next integration boundary.
Audit an instrumented run with `./scripts/audit-i960-clean-runtime.sh`; it
fails if any observed PC lies beyond the generated-code extent.
The current eight-second baseline visits 564 distinct PCs, all within the
generated `0x00000000-0x00002520` range.

The first standalone C slice is the reset routine. Its candidate artifacts are
`von/build/i960/reconstructed_reset.elf`, `reconstructed_reset.bin`, and
`reconstructed_reset.lst`; compare it with:

```sh
python3 von/tools/reconstruction_progress.py \
  --compare maincpu/reset_startup \
  --original von/build/disasm/vonj-maincpu.bin \
  --generated von/build/i960/reconstructed_reset.bin
```

The current result is 35 of 184 bytes equal, so this slice remains
provisional.

Coverage has two deliberately separate reports:

```sh
# Strict headline metric: only byte-for-byte C matches.
python3 von/tools/reconstruction_progress.py --report

# C-represented slices with evidence; never substitute this for the headline.
python3 von/tools/reconstruction_progress.py --semantic-report
```

The current compiler has not yet been calibrated to reproduce the original
i960 ABI and native instruction selection. Production C recovery therefore
continues with behavioral tests; do not add isolated wrapper/stub candidates
solely to obtain a low-quality byte comparison.

Trace the reconstructed loader milestones with:

```sh
VON_I960_STATE_LOG=/tmp/von-i960-state.log SDL_VIDEODRIVER=dummy \
  ./scripts/run-i960-reconstructed.sh -video none -sound none -oslog \
  -autoboot_script von/tools/trace_i960_reconstructed_state.lua \
  -seconds_to_run 5 -skip_gameinfo
```

The loader core is complete when the trace reports `init=494e4954` and
`texture_status=00000000`.

Generate a readable disassembly of the original `vonj` host ROM with:

```sh
./scripts/remote-disasm-i960.sh
```

This writes `von/build/disasm/vonj-maincpu.lst` (about 18 MiB). The reset
entry is at `0x00000930`; the focused startup slice can be viewed with:

```sh
sed -n '430,475p' von/build/disasm/vonj-maincpu.lst
```

The compiler-generated listing for the C reconstruction is
`von/build/i960/reconstructed.lst`. It is much smaller and includes the
reconstructed symbol names, while the original ROM listing is raw-address
disassembly and still needs function-boundary annotations.

The reconstructed image currently covers the trace-confirmed I/O self-test,
SHARC upload, geometry upload/setup, command-window initialization, texture
initialization, and frame-synchronized startup pipeline. It remains separate
from the smoke prototype and returns to a heartbeat after completing that
bounded pipeline; the attract scheduler is not yet reconstructed.

The build uses `ghcr.io/nkito/i960_sbc:latest`, which provides an
`i960-elf` GCC/binutils toolchain. The image is pinned by the Docker registry
digest in the build script so the compiler can be reproduced later.

Outputs are written below `von/build/i960/`:

- `prototype.elf`: linked i960 ELF with symbols
- `prototype.bin`: raw linked image
- `prototype.lst`: i960 disassembly of the generated image
- `reconstructed.elf`: linked C reconstruction with symbols
- `reconstructed.bin`: raw C reconstruction image
- `reconstructed.lst`: i960 disassembly of the C reconstruction
- `reconstructed_reset.elf`: standalone reset-slice ELF
- `reconstructed_reset.bin`: standalone reset-slice binary
- `reconstructed_reset.lst`: standalone reset-slice disassembly

The linker layout is a first approximation of the Model 2 address map. The
startup table at address zero follows the i960 Kx reset structure, while the
runtime entry point only records a heartbeat in host RAM and loops.

The prototype also parses the recovered text-record table from `main_data` at
`0x02ea2918` and renders its records into the Model 2 tile RAM window at
`0x01000000`. The recovered `(row << 6) + column` position formula and
`0x8000 | ASCII` encoding are validated against the original `vonj` host trace.
