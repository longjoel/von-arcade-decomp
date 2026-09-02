#!/usr/bin/env python3
"""Test the recovered frame-transpose update of SHARC opcode 0x24."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_24.c"
SEED_SOURCE = ROOT / "von/i960/recovered_sharc_opcode_1f.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-24-") as directory:
        library = Path(directory) / "libopcode_24.so"
        subprocess.run(
            ["cc", "-std=c99", "-O2", "-fPIC", "-shared", str(SOURCE),
             str(SEED_SOURCE), "-o", str(library)],
            check=True,
        )
        update = ctypes.CDLL(str(library)).recovered_sharc_opcode_24_update_state
        update.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        update.restype = None

        identity = (
            0x3f800000, 0, 0, 0, 0x3f800000, 0,
            0, 0, 0x3f800000,
        )
        seed = (
            0x3f800000, 0x40000000, 0x40400000,
            0x40800000, 0x40a00000, 0x40c00000,
            0x40e00000, 0x41000000, 0x41100000,
        )
        vectors = (
            ((0x3f800000, 0, 0), identity,
             (0, 0, 0xbf800000, 0, 0x3f800000, 0,
              0x3f800000, 0, 0)),
            ((0, 0, 0x3f800000), identity, identity),
            ((0x3f800000, 0, 0), seed,
             (0xc0e00000, 0xc1000000, 0xc1100000,
              0x40800000, 0x40a00000, 0x40c00000,
              0x3f800000, 0x40000000, 0x40400000)),
            ((0x3f800000, 0x40000000, 0x40400000), identity,
             (0x3f72dce8, 0, 0xbea1e89b,
              0xbe2d166c, 0x3f585c07, 0xbf01d0d1,
              0x3e88d677, 0x3f08d677, 0x3f4d41b2)),
        )
        for values, state, expected in vectors:
            input_words = (ctypes.c_uint32 * 3)(*values)
            state_words = (ctypes.c_uint32 * 9)(*state)
            output_words = (ctypes.c_uint32 * 9)()
            update(input_words, state_words, output_words)
            if tuple(output_words) != expected:
                raise SystemExit(
                    f"opcode 0x24 state mismatch: {values!r} -> "
                    f"{tuple(output_words)!r}; expected {expected!r}"
                )

    print("recovered SHARC opcode-0x24 frame transpose: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
