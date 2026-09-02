#!/usr/bin/env python3
"""Test the reduced state-3 classifier from the i960 object helper."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_state_three.c"


def expected(role: int, caller: int, mode: int) -> int:
    if role == 4:
        if caller > 5:
            return 7
        if mode & 2 or (caller <= 2 and mode & 4):
            return 9
        return 7
    return 9 if caller <= 2 and mode & 4 else 7


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-object-state-three-") as directory:
        library = Path(directory) / "object-state-three.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        route = recovered.recovered_object_state_three_route
        route.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        route.restype = ctypes.c_uint32

        vectors = 0
        for related in range(10):
            for role in range(7):
                for caller in range(10):
                    for mode in range(8):
                        for global_state in (0, 3):
                            transition = ctypes.c_uint32(0xA5A5A5A5)
                            changed = route(
                                related,
                                role,
                                caller,
                                mode,
                                0x40690000,
                                global_state,
                                0xA5A5A5A5,
                                ctypes.byref(transition),
                            )
                            assert changed == 1
                            want = expected(role, caller, mode)
                            if transition.value != want:
                                raise SystemExit(
                                    f"state-3 mismatch related={related} role={role} "
                                    f"caller={caller} mode={mode} global={global_state}: "
                                    f"{transition.value} != {want}"
                                )
                            vectors += 1

    print(f"recovered object-state three vectors: {vectors} ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
