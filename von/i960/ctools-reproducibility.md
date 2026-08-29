# Intel CTOOLS Reproducibility Track

The byte-matching experiment uses the preserved Intel CTOOLS 5.0 distribution
from [`biggestsonicfan/i960-CTOOLS-with-NINDY`](https://github.com/biggestsonicfan/i960-CTOOLS-with-NINDY).

## Pinned input

```text
repository: https://github.com/biggestsonicfan/i960-CTOOLS-with-NINDY.git
commit:     0d331fc558615cd3049566fdc0e1a4f90b3bd067
host kit:   i386-nbsd1-ctools
compiler:   bin/gcc960
assembler:  bin/asm960
linker:     bin/lnk960
converter:  bin/rom960
target:     i960KB (Model 2 host CPU)
```

The supplied Unix executables are NetBSD/i386 `a.out` programs, not Linux
executables. The repository documents NetBSD/i386 plus `compat12` as the
supported execution environment. The Windows 95 kit is not used: introducing
Wine would add an extra compatibility layer and weaken reproducibility.

## Required runner

Provision one immutable NetBSD/i386 VM image on `drone0` with:

```sh
pkg_add git-base mozilla-rootcerts compat12
```

Inside that VM, clone the exact commit above, make the executables under
`i386-nbsd1-ctools/bin` and the compiler passes under
`i386-nbsd1-ctools/lib` executable, and record:

```sh
uname -a
sha256 -q i386-nbsd1-ctools/bin/gcc960
sha256 -q i386-nbsd1-ctools/bin/asm960
sha256 -q i386-nbsd1-ctools/bin/lnk960
sha256 -q i386-nbsd1-ctools/bin/rom960
```

Those four hashes, the VM image checksum, this Git commit, and each source
file checksum are part of the build identity.

## First acceptance experiment

Do not attempt the entire ROM first. Compile the 184-byte reset slice at
`0x00000930–0x000009e8` with CTOOLS, link it at `0x930`, convert its COFF
output with `rom960`, and compare exactly against the extracted original:

```sh
cmp -l generated-reset.bin original-reset.bin
sha256sum generated-reset.bin original-reset.bin
```

The result is useful whether it matches or not: it reveals the original
compiler's calling convention, prologue/epilogue shape, and instruction
selection without conflating those issues with the full image layout. Only a
zero-difference result promotes the slice to `byte-validated`.

## Reproducibility rule

The eventual `scripts/remote-ctools-build.sh` must reject an unpinned CTOOLS
checkout or runner hash, emit a manifest containing all inputs and output
hashes, and run the build twice in fresh output directories. The two generated
binary hashes must be equal before any comparison with the arcade ROM is
reported.
