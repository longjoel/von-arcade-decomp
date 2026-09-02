#!/usr/bin/env python3
"""Test the state-1 role/timing classifier."""

from __future__ import annotations

import ctypes
import os
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_state_one.c"


def bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def expected(timer: float, caller: int, mode: int, role: int) -> int:
    if not mode & 2 or role <= 6:
        return 7
    if timer < 0.0:
        return 8
    return 9 if caller <= 2 and mode & 4 else 8


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-object-state-one-") as directory:
        library = Path(directory) / "object-state-one.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        route = recovered.recovered_object_state_one_route
        route.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        route.restype = ctypes.c_uint32

        timers = (-1.0, -0.0, 0.0, 3.390625, 100.0)
        vectors = 0
        for timer in timers:
            for caller in range(10):
                for mode in range(8):
                    for role in range(8):
                        transition = ctypes.c_uint32(0xA5A5A5A5)
                        assert route(bits(timer), caller, mode, role, ctypes.byref(transition)) == 1
                        want = expected(timer, caller, mode, role)
                        if transition.value != want:
                            raise SystemExit(
                                f"state-1 mismatch timer={timer} caller={caller} "
                                f"mode={mode} role={role}: {transition.value} != {want}"
                            )
                        vectors += 1

    print(f"recovered object-state one vectors: {vectors} ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
