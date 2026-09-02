#!/usr/bin/env python3
"""Test the semantic model of SHARC opcode 0x0c normalization."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_0c.c"
SEED_SOURCE = ROOT / "von/i960/recovered_sharc_opcode_1f.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-0c-") as directory:
        library = Path(directory) / "libopcode_0c.so"
        subprocess.run(
            ["cc", "-std=c99", "-O2", "-fPIC", "-shared", str(SOURCE),
             str(SEED_SOURCE), "-lm", "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        normalize = lib.recovered_sharc_opcode_0c_normalize
        normalize.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)
        ]
        normalize.restype = None

        vectors = (
            ((0x40400000, 0x40800000, 0x41400000),
             (0x3e6c4ec4, 0x3e9d89d8, 0x3f6c4ec4)),
            ((0, 0, 0), (0xffffffff, 0xffffffff, 0xffffffff)),
            # Live interpreter-backed rounding probe vectors.
            ((0x3f800001, 0, 0), (0x3f800000, 0x00000000, 0x00000000)),
            ((0x3f800000, 0x3f800001, 0),
             (0x3f3504f3, 0x3f3504f4, 0x00000000)),
            ((0x3f800001, 0xbf800000, 0),
             (0x3f3504f4, 0xbf3504f3, 0x00000000)),
            ((0x4b800000, 0, 0), (0x3f800000, 0x00000000, 0x00000000)),
            ((0x4b800000, 0x4b800000, 0x4b800001),
             (0x3f13cd3a, 0x3f13cd3a, 0x3f13cd3b)),
            # Direct post-boot edge capture.
            ((0x80000000, 0, 0), (0xffffffff, 0xffffffff, 0xffffffff)),
            ((0x00000001, 0, 0), (0xffffffff, 0xffffffff, 0xffffffff)),
            ((0x7f800000, 0, 0), (0x7f800000, 0, 0)),
            ((0x7fc00000, 0, 0), (0xffffffff, 0xffffffff, 0xffffffff)),
            ((0x3f800000, 0x7f800000, 0),
             (0x1f800000, 0x7f800000, 0)),
            ((0, 0x7f800000, 0), (0, 0x7f800000, 0)),
            ((0xff800000, 0, 0), (0xff800000, 0, 0)),
            ((0x7f800000, 0x7f800000, 0),
             (0x7f800000, 0x7f800000, 0)),
            ((0x3f800000, 0x00000001, 0),
             (0x3f800000, 0x00000001, 0)),
        )
        for values, expected in vectors:
            input_words = (ctypes.c_uint32 * 3)(*values)
            output_words = (ctypes.c_uint32 * 3)()
            normalize(input_words, output_words)
            actual = tuple(output_words)
            if actual != expected:
                raise SystemExit(
                    f"opcode 0x0c mismatch: {values!r} -> "
                    f"{tuple(f'0x{x:08x}' for x in actual)}, "
                    f"expected {tuple(f'0x{x:08x}' for x in expected)}"
                )

    print("recovered SHARC opcode-0x0c normalization vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
