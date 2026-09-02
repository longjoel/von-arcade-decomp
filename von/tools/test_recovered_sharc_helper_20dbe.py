#!/usr/bin/env python3
"""Validate the bounded numerical model of SHARC helper 0x20dbe/0x20dc4."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_helper_20dbe.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-reduction-") as directory:
        library = Path(directory) / "libreduction.so"
        subprocess.run(
            ["cc", "-std=c99", "-O2", "-fPIC", "-shared", str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        sine = lib.recovered_sharc_helper_20dc4_sine
        sine.argtypes = [ctypes.c_uint32, ctypes.c_int]
        sine.restype = ctypes.c_uint32
        cosine = lib.recovered_sharc_helper_20dbe_cosine
        cosine.argtypes = [ctypes.c_uint32, ctypes.c_int]
        cosine.restype = ctypes.c_uint32

        # These are the four endpoint states captured from the live ROM path.
        expected = (
            (0x00000000, 0, 0x00000000),
            (0x3FC9116D, 0, 0x3F800000),
            (0x40490FDB, 0, 0xB3BBBD00),
            (0x4049116D, 1, 0x38C92EEF),
        )
        for magnitude, negative, result in expected:
            actual = sine(magnitude, negative)
            if actual != result:
                raise SystemExit(
                    f"reduction endpoint {magnitude:#010x}/{negative} "
                    f"was {actual:#010x}, expected {result:#010x}"
                )

        cosine_expected = (
            (0x00000000, 0, 0x3F7FFFFF),
            (0x3F49116D, 0, 0x3F3503D8),
            (0x3FC9116D, 0, 0xB8492EEF),
            (0x4016CD12, 0, 0xBF35084A),
            (0x40490FDB, 0, 0xBF7FFFFF),
            (0x4049116D, 1, 0xBF7FFFFF),
            (0x4016CD12, 1, 0xBF35084A),
            (0x3FC9116D, 1, 0xB8492EEF),
        )
        for magnitude, negative, result in cosine_expected:
            actual = cosine(magnitude, negative)
            if actual != result:
                raise SystemExit(
                    f"cosine endpoint {magnitude:#010x}/{negative} "
                    f"was {actual:#010x}, expected {result:#010x}"
                )

        # Full signed quadrant sweep, using the absolute angle words observed
        # at the shared reducer's 0x20dca entry.
        sweep_magnitudes = (
            0x00000000, 0x3EC9116D, 0x3F49116D, 0x3F96CD12,
            0x3FC9116D, 0x3FFB55C8, 0x4016CD12, 0x402FEF3F,
            0x4049116D, 0x402FEF3F, 0x4016CD12, 0x3FFB55C8,
            0x3FC9116D, 0x3F96CD12, 0x3F49116D, 0x3EC9116D,
        )
        sine_sweep = (
            0x00000000, 0x3EC3F089, 0x3F350610, 0x3F6C8446,
            0x3F800000, 0x3F6C81DE, 0x3F35019C, 0x3EC3E4F0,
            0x38C92EEF, 0xBEC3E4F0, 0xBF35019C, 0xBF6C81DE,
            0xBF800000, 0xBF6C8446, 0xBF350610, 0xBEC3F089,
        )
        cosine_sweep = (
            0x3F7FFFFF, 0x3F6C8310, 0x3F3503D8, 0x3EC3EAB8,
            0xB8492EEF, 0xBEC3F657, 0xBF35084A, 0xBF6C8578,
            0xBF7FFFFF, 0xBF6C8578, 0xBF35084A, 0xBEC3F657,
            0xB8492EEF, 0x3EC3EAB8, 0x3F3503D8, 0x3F6C8310,
        )
        for index, (magnitude, sine_result, cosine_result) in enumerate(
            zip(sweep_magnitudes, sine_sweep, cosine_sweep)
        ):
            negative = index >= 8
            if sine(magnitude, negative) != sine_result:
                raise SystemExit(f"sine sweep sample {index} does not match")
            if cosine(magnitude, negative) != cosine_result:
                raise SystemExit(f"cosine sweep sample {index} does not match")

    print("PASS: bounded SHARC 0x20dbe/0x20dc4 numerical reduction model and quadrant sweep")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
