#!/usr/bin/env python3
"""Test the timing/mode classifier recovered from object state 5."""

from __future__ import annotations

import ctypes
import os
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_state_five.c"


def bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def expected(timer: float, caller: int, mode: int) -> int:
    if timer < 0.0:
        return 8 if mode & 2 else 7
    if timer < 3.640625:
        return 9 if caller > 3 and mode & 4 else 7
    if caller == 0:
        return 7
    if caller <= 4:
        return 9 if mode & 4 else 7
    if mode & 2:
        return 8
    return 9 if mode & 4 else 7


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-object-state-five-") as directory:
        library = Path(directory) / "object-state-five.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        route = recovered.recovered_object_state_five_route
        route.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        route.restype = ctypes.c_uint32

        timers = (-1.0, -0.0, 0.0, 3.640625 - 0.0001, 3.640625, 10.0)
        vectors = 0
        for timer in timers:
            for caller in range(10):
                for mode in range(8):
                    transition = ctypes.c_uint32(0xA5A5A5A5)
                    assert route(bits(timer), caller, mode, ctypes.byref(transition)) == 1
                    actual = transition.value
                    want = expected(timer, caller, mode)
                    if actual != want:
                        raise SystemExit(
                            f"state-5 mismatch timer={timer} caller={caller} mode={mode}: "
                            f"{actual} != {want}"
                        )
                    vectors += 1

    print(f"recovered object-state five vectors: {vectors} ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
