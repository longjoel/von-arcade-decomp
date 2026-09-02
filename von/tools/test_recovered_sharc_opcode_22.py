#!/usr/bin/env python3
"""Test the proven affine kernel of SHARC opcode 0x22."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_22.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-22-") as directory:
        library = Path(directory) / "libopcode_22.so"
        subprocess.run(
            ["cc", "-std=c99", "-O2", "-fPIC", "-shared", str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        affine = lib.recovered_sharc_opcode_22_affine
        affine.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        affine.restype = None
        clipped = lib.recovered_sharc_opcode_22_clipped
        clipped.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ]
        clipped.restype = ctypes.c_int

        identity = (0x3f800000, 0, 0, 0, 0x3f800000, 0,
                    0, 0, 0x3f800000, 0, 0, 0)
        input_words = (ctypes.c_uint32 * 3)(0x3f800000, 0x40000000, 0x40400000)
        state_words = (ctypes.c_uint32 * 12)(*identity)
        output_words = (ctypes.c_uint32 * 3)()
        affine(input_words, state_words, output_words)
        if tuple(output_words) != (0x40400000, 0x3f800000, 0x40000000):
            raise SystemExit(f"identity affine mismatch: {tuple(output_words)!r}")

        diagonal = (0x40000000, 0, 0, 0, 0x40400000, 0,
                    0, 0, 0x40800000, 0x3f800000, 0x40000000, 0x40400000)
        state_words = (ctypes.c_uint32 * 12)(*diagonal)
        affine(input_words, state_words, output_words)
        if tuple(output_words) != (0x41700000, 0x40400000, 0x41000000):
            raise SystemExit(f"diagonal affine mismatch: {tuple(output_words)!r}")

        wide = (0x3f800000, 0x3f800000, 0x42c80000,
                0xc2c80000, 0x42c80000, 0xc2c80000)
        clip_state = (ctypes.c_uint32 * 12)(*identity)
        input_words = (ctypes.c_uint32 * 4)(0x3f800000, 0x40000000,
                                             0x40400000, 0)
        clip_words = (ctypes.c_uint32 * 6)(*wide)
        result = ctypes.c_uint32()
        if clipped(input_words, clip_state, clip_words, ctypes.byref(result)) != 0:
            raise SystemExit("wide clip parameters unexpectedly rejected")
        if result.value != 0x40400000:
            raise SystemExit(f"normal clipped result mismatch: {result.value:#x}")

        asymmetric = (0x40000000, 0x40400000, 0x42c80000,
                      0xc2c80000, 0x42c80000, 0xc2c80000)
        nonzero_w = (ctypes.c_uint32 * 4)(0x3f800000, 0x40000000,
                                           0x40400000, 0x3f800000)
        if clipped(nonzero_w, clip_state,
                   (ctypes.c_uint32 * 6)(*asymmetric), ctypes.byref(result)) != 0:
            raise SystemExit("nonzero-w clip parameters unexpectedly rejected")
        if result.value != 0x40400000:
            raise SystemExit(f"nonzero-w clipped result mismatch: {result.value:#x}")

        zero_depth = (ctypes.c_uint32 * 4)(0x3f800000, 0x40000000,
                                           0x00000000, 0)
        if clipped(zero_depth, clip_state, (ctypes.c_uint32 * 6)(*wide),
                   ctypes.byref(result)) != 0 or result.value != 0:
            raise SystemExit("zero affine depth did not fall through as zero")

        nan_depth = (ctypes.c_uint32 * 4)(0x3f800000, 0x40000000,
                                          0xffffffff, 0)
        if clipped(nan_depth, clip_state, (ctypes.c_uint32 * 6)(*wide),
                   ctypes.byref(result)) != 0:
            raise SystemExit("NaN affine depth did not follow unordered path")
        result_float = ctypes.c_float.from_buffer_copy(
            result.value.to_bytes(4, "little")
        ).value
        if not math.isnan(result_float):
            raise SystemExit("NaN affine depth did not publish a NaN result")

        for offset in range(2, 6):
            bounds = list(wide)
            bounds[offset] = 0xc2c80000 if offset in (2, 4) else 0x42c80000
            clip_words = (ctypes.c_uint32 * 6)(*bounds)
            if clipped(input_words, clip_state, clip_words,
                       ctypes.byref(result)) != -1:
                raise SystemExit(f"clip threshold offset {offset} did not reject")

        negative_depth = (ctypes.c_uint32 * 4)(0x3f800000, 0x40000000,
                                                0xc0400000, 0)
        if clipped(negative_depth, clip_state, (ctypes.c_uint32 * 6)(*wide),
                   ctypes.byref(result)) != -2 or result.value != 0xc0000000:
            raise SystemExit("negative affine depth did not select -2 fallback")

    print("recovered SHARC opcode-0x22 affine and clip kernels: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
