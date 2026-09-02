#!/usr/bin/env python3
"""Check the readable rational candidate for SHARC helper 0x20d68."""

from __future__ import annotations

import ctypes
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_helper_20d68_candidate.c"


def bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def ulp_distance(left: int, right: int) -> int:
    # The vectors are finite; raw-word distance is exact for the captured
    # negative results as well as the positive ones.
    return abs(left - right)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-20d68-candidate-") as directory:
        library = Path(directory) / "libhelper.so"
        subprocess.run(
            ["cc", "-std=c99", "-O2", "-ffp-contract=off", "-fPIC", "-shared",
             str(SOURCE), "-o", str(library)],
            check=True,
        )
        helper = ctypes.CDLL(str(library)).recovered_sharc_helper_20d68_candidate
        helper.argtypes = [ctypes.c_float, ctypes.c_float]
        helper.restype = ctypes.c_float

        # ROM words captured at 0x20db4 for the finite-ratio and LOGB-boundary
        # sweeps.  The normal finite range-reduction path and the normal-value
        # endpoint guard match exactly. NaN canonicalization and subnormal
        # flushing are covered below; direct infinity input remains out of
        # scope.
        vectors = (
            (1.0, 2.0, 0x3eed6338, 0),
            (2.0, 1.0, 0x3f8db70d, 0),
            (1.0, 4.0, 0x3e7adbb0, 0),
            (4.0, 1.0, 0x3fa9b465, 0),
            (1.0, 1.0, 0x3f490fda, 0),
            # Signed quadrant samples from the same helper sweep.
            (1.0, -2.0, 0x402b6374, 0),
            (-2.0, 1.0, 0xbf8db70d, 0),
            # Independent asymmetric/signed sweep captured through MAME's
            # helper trace.
            (0.5, 3.0, 0x3e291cbc, 0),
            (3.0, 0.5, 0x3fb3ec44, 0),
            (0.25, 5.0, 0x3d4ca12d, 0),
            (5.0, 0.25, 0x3fc2aad2, 0),
            (-0.5, 3.0, 0xbe291cbc, 0),
            (3.0, -0.5, 0x3fde3372, 0),
            (-1.0, 6.0, 0xbe291cbc, 0),
            (6.0, -1.0, 0x3fde3372, 0),
            (struct.unpack("<f", struct.pack("<I", 0x7d800000))[0],
             1.0, 0x3fc90fdb, 0),
            (1.0,
             struct.unpack("<f", struct.pack("<I", 0x7d800000))[0],
             0x00000000, 0),
            (struct.unpack("<f", struct.pack("<I", 0x7d000000))[0],
             1.0, 0x3fc90fdb, 0),
            (1.0,
             struct.unpack("<f", struct.pack("<I", 0x7d000000))[0],
             0x02000000, 0),
            (struct.unpack("<f", struct.pack("<I", 0x7fc00000))[0],
             1.0, 0xffffffff, 0),
            (1.0,
             struct.unpack("<f", struct.pack("<I", 0x7fc00000))[0],
             0xffffffff, 0),
            (struct.unpack("<f", struct.pack("<I", 0x00000001))[0],
             1.0, 0x00000000, 0),
            (1.0,
             struct.unpack("<f", struct.pack("<I", 0x00000001))[0],
             0x3fc90fdb, 0),
        )
        for first, second, expected, allowed in vectors:
            actual = bits(float(helper(first, second)))
            if ulp_distance(actual, expected) > allowed:
                raise SystemExit(
                    f"candidate mismatch ({first},{second}): "
                    f"0x{actual:08x}, expected 0x{expected:08x} "
                    f"within {allowed} ULP"
                )

    print("PASS: SHARC 0x20d68 rational candidate stays within captured bounds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
