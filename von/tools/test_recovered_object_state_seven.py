#!/usr/bin/env python3
"""Test the state-7 global/related-object classifier."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_state_seven.c"


def expected(global_state: int, related: int, caller: int, mode: int) -> int:
    if related != 4:
        return 7
    if global_state <= 3:
        return 9 if mode & 4 else 7
    if caller <= 3 and mode & 2:
        return 8
    return 9 if caller > 1 and mode & 4 else 7


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-object-state-seven-") as directory:
        library = Path(directory) / "object-state-seven.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        route = recovered.recovered_object_state_seven_route
        route.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        route.restype = ctypes.c_uint32

        vectors = 0
        for global_state in range(8):
            for related in range(8):
                for caller in range(10):
                    for mode in range(8):
                        transition = ctypes.c_uint32(0xA5A5A5A5)
                        assert route(
                            global_state, related, caller, mode,
                            ctypes.byref(transition),
                        ) == 1
                        want = expected(global_state, related, caller, mode)
                        if transition.value != want:
                            raise SystemExit(
                                f"state-7 mismatch global={global_state} related={related} "
                                f"caller={caller} mode={mode}: {transition.value} != {want}"
                            )
                        vectors += 1

    print(f"recovered object-state seven vectors: {vectors} ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
