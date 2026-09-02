#!/usr/bin/env python3
"""Exhaustively test the profile constant table recovered from 0x28840."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_profile.c"


class Constants(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in ("first", "second", "third")]


EXPECTED = (
    (0x3F000000, 0x3F4CCCCD, 0x3E4CCCCD),
    (0x3EE66666, 0x3F400000, 0x3E800000),
    (0x3EE66666, 0x3F266666, 0x3EB33333),
    (0x3EB33333, 0x3F0CCCCD, 0x3EE66666),
    (0x3EB33333, 0x3EE66666, 0x3F0CCCCD),
    (0x3F800000, 0x3F59999A, 0x00000000),
    (0x3F733333, 0x3F59999A, 0x00000000),
    (0x3F59999A, 0x3F59999A, 0x3D4CCCCD),
    (0x3F400000, 0x3F59999A, 0x3DCCCCCD),
)
DEFAULT = (0x3F0CCCCD, 0x3F59999A, 0x3E19999A)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-geometry-profile-") as directory:
        library = Path(directory) / "profile.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        select = recovered.recovered_geometry_profile_constants
        select.argtypes = [
            ctypes.c_uint8,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        select.restype = ctypes.c_int

        vectors = 0
        for backup in range(256):
            first = ctypes.c_uint32()
            second = ctypes.c_uint32()
            third = ctypes.c_uint32()
            direct = select(backup, ctypes.byref(first), ctypes.byref(second), ctypes.byref(third))
            actual = (first.value, second.value, third.value)
            expected = EXPECTED[backup - 1] if 1 <= backup <= 9 else DEFAULT
            if (direct == 1) != (1 <= backup <= 9) or actual != expected:
                raise SystemExit(
                    f"profile mismatch backup={backup}: direct={direct} {actual!r} != {expected!r}"
                )
            vectors += 1

    print(f"PASS: {vectors} geometry profile vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
