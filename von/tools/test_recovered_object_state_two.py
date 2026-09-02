#!/usr/bin/env python3
"""Test the state-2 global/timing classifier."""

from __future__ import annotations

import ctypes
import os
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_state_two.c"


def bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def expected(timer: float, caller: int, mode: int, global_state: int, role: int) -> int:
    if global_state == 5 and mode & 2:
        return 8
    if timer < 0.0:
        if caller <= 4 and mode & 4:
            return 9
        if caller <= 2 or not mode & 2 or role <= 6:
            return 7
        return 8
    return 9 if caller > 2 and mode & 4 else 7


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-object-state-two-") as directory:
        library = Path(directory) / "object-state-two.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        route = recovered.recovered_object_state_two_route
        route.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        route.restype = ctypes.c_uint32

        timers = (-1.0, -0.0, 0.0, 3.79296875, 100.0)
        vectors = 0
        for timer in timers:
            for caller in range(10):
                for mode in range(8):
                    for global_state in (0, 5, 6):
                        for role in range(8):
                            transition = ctypes.c_uint32(0xA5A5A5A5)
                            assert route(
                                bits(timer), caller, mode, global_state, role,
                                ctypes.byref(transition),
                            ) == 1
                            want = expected(timer, caller, mode, global_state, role)
                            if transition.value != want:
                                raise SystemExit(
                                    f"state-2 mismatch timer={timer} caller={caller} "
                                    f"mode={mode} global={global_state} role={role}: "
                                    f"{transition.value} != {want}"
                                )
                            vectors += 1

    print(f"recovered object-state two vectors: {vectors} ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
