#!/usr/bin/env python3
"""Test the proven normalization and frame-update kernels of opcode 0x23."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_23.c"
SEED_SOURCE = ROOT / "von/i960/recovered_sharc_opcode_1f.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-23-") as directory:
        library = Path(directory) / "libopcode_23.so"
        subprocess.run(
            ["cc", "-std=c99", "-O2", "-fPIC", "-shared", str(SOURCE),
             str(SEED_SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        normalize = lib.recovered_sharc_opcode_23_normalized_direction
        normalize.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)
        ]
        normalize.restype = None
        update = lib.recovered_sharc_opcode_23_update_state
        update.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        update.restype = None

        vectors = (
            ((0x3f800000, 0, 0), (0x3f800000, 0x80000000, 0)),
            ((0, 0x3f800000, 0), (0, 0xbf800000, 0)),
            ((0, 0, 0x3f800000), (0, 0x80000000, 0x3f800000)),
            ((0x40400000, 0x40800000, 0x41400000),
             (0x3e6c4ec4, 0xbe9d89d8, 0x3f6c4ec4)),
        )
        for values, expected in vectors:
            input_words = (ctypes.c_uint32 * 3)(*values)
            output_words = (ctypes.c_uint32 * 3)()
            normalize(input_words, output_words)
            if tuple(output_words) != expected:
                raise SystemExit(
                    f"opcode 0x23 mismatch: {values!r} -> {tuple(output_words)!r}; "
                    f"expected {expected!r}"
                )

        identity = (
            0x3f800000, 0, 0, 0, 0x3f800000, 0,
            0, 0, 0x3f800000,
        )
        seed_a = (
            0x3f800000, 0x40000000, 0x40400000,
            0x40800000, 0x40a00000, 0x40c00000,
            0x40e00000, 0x41000000, 0x41100000,
        )
        state_vectors = (
            ((0x3f800000, 0, 0), identity,
             (0, 0, 0x3f800000, 0, 0x3f800000, 0,
              0xbf800000, 0, 0)),
            ((0, 0, 0x3f800000), identity, identity),
            ((0x3f800000, 0, 0), seed_a,
             (0x40e00000, 0x41000000, 0x41100000,
              0x40800000, 0x40a00000, 0x40c00000,
              0xbf800000, 0xc0000000, 0xc0400000)),
            ((0x3f800000, 0x40000000, 0x40400000), identity,
             (0x3f72dce8, 0xbe2d166c, 0x3e88d677,
              0, 0x3f585c07, 0x3f08d677,
              0xbea1e89b, 0xbf01d0d1, 0x3f4d41b2)),
        )
        for values, state, expected in state_vectors:
            input_words = (ctypes.c_uint32 * 3)(*values)
            state_words = (ctypes.c_uint32 * 9)(*state)
            output_words = (ctypes.c_uint32 * 9)()
            update(input_words, state_words, output_words)
            if tuple(output_words) != expected:
                raise SystemExit(
                    f"opcode 0x23 state mismatch: {values!r} -> "
                    f"{tuple(output_words)!r}; expected {expected!r}"
                )

    print("recovered SHARC opcode-0x23 normalization and frame update: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
