# i960 Host ROM Prototype

This directory contains the first native i960 build target for the Virtual-On
host ROM replacement. It is intentionally a hardware smoke test, not a game
implementation.

Build it from the project root:

```sh
./scripts/i960-build.sh
```

The build uses `ghcr.io/nkito/i960_sbc:latest`, which provides an
`i960-elf` GCC/binutils toolchain. The image is pinned by the Docker registry
digest in the build script so the compiler can be reproduced later.

Outputs are written below `von/build/i960/`:

- `prototype.elf`: linked i960 ELF with symbols
- `prototype.bin`: raw linked image
- `prototype.lst`: i960 disassembly of the generated image

The linker layout is a first approximation of the Model 2 address map. The
startup table at address zero follows the i960 Kx reset structure, while the
runtime entry point only records a heartbeat in host RAM and loops.
