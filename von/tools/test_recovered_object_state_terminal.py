#!/usr/bin/env python3
"""Test the unconditional state-8/state-9 routes in the object helper."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_state_terminal.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-object-terminal-") as directory:
        library = Path(directory) / "object-terminal.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        route = recovered.recovered_object_state_terminal_route
        route.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        route.restype = ctypes.c_uint32

        for state in range(256):
            transition = ctypes.c_uint32(0xA5A5A5A5)
            changed = route(state, ctypes.byref(transition))
            expected = state in (8, 9)
            assert bool(changed) == expected
            assert transition.value == (7 if expected else 0xA5A5A5A5)

    print("recovered object-state terminal vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
