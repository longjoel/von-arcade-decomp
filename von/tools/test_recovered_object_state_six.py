#!/usr/bin/env python3
"""Test the state-6 classifier and common-tail remap."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_state_six.c"


def expected(role: int, mode: int, tag: int, state: int, substate: int) -> int:
    if role in (5, 6):
        selected = 1
    elif role in (0, 4) or role >= 7:
        selected = 8 if mode & 2 else 7
    elif tag == 31 and state == 3 and substate in (1, 3, 4, 6, 7):
        selected = 8 if mode & 2 and substate in (3, 6) else 7
    else:
        selected = 8 if mode & 2 else 7
    if tag == 31 and state == 3:
        return {7: 10, 8: 11}.get(selected, selected)
    return selected


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-object-state-six-") as directory:
        library = Path(directory) / "object-state-six.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        route = recovered.recovered_object_state_six_route
        route.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        route.restype = ctypes.c_uint32

        vectors = 0
        for role in range(12):
            for mode in range(8):
                for tag in (0, 31, 32):
                    for state in range(8):
                        for substate in range(9):
                            transition = ctypes.c_uint32(0xA5A5A5A5)
                            assert route(
                                role, mode, tag, state, substate,
                                ctypes.byref(transition),
                            ) == 1
                            want = expected(role, mode, tag, state, substate)
                            if transition.value != want:
                                raise SystemExit(
                                    f"state-6 mismatch role={role} mode={mode} "
                                    f"tag={tag} state={state} substate={substate}: "
                                    f"{transition.value} != {want}"
                                )
                            vectors += 1

    print(f"recovered object-state six vectors: {vectors} ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
