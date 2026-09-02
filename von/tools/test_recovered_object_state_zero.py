#!/usr/bin/env python3
"""Test state 0, including its intentional no-write fallthroughs."""

from __future__ import annotations

import ctypes
import os
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_state_zero.c"


def bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def expected(timer: float, mode: int, role: int, obj: int) -> tuple[bool, int]:
    if timer >= 0.0 or not mode & 2:
        return True, 7
    if role in (1, 2, 3):
        return False, 0
    if obj >= 8:
        return True, 8
    if role == 4:
        return (obj <= 5, 8)
    if role in (5, 6):
        return (obj <= 3, 8)
    return False, 0


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-object-state-zero-") as directory:
        library = Path(directory) / "object-state-zero.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        route = recovered.recovered_object_state_zero_route
        route.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        route.restype = ctypes.c_uint32

        vectors = 0
        for timer in (-1.0, -0.0, 0.0, 3.640625, 100.0):
            for mode in range(8):
                for role in range(10):
                    for obj in range(12):
                        transition = ctypes.c_uint32(0xA5A5A5A5)
                        changed = bool(route(bits(timer), mode, role, obj, ctypes.byref(transition)))
                        want_changed, want_value = expected(timer, mode, role, obj)
                        if (changed, transition.value) != (
                            want_changed,
                            want_value if want_changed else 0xA5A5A5A5,
                        ):
                            raise SystemExit(
                                f"state-0 mismatch timer={timer} mode={mode} role={role} "
                                f"object={obj}: {(changed, transition.value)!r} != "
                                f"{(want_changed, want_value)!r}"
                            )
                        vectors += 1

    print(f"recovered object-state zero vectors: {vectors} ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
