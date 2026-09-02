#!/usr/bin/env python3
"""Test the random-residue role table used before the object helper call."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_state_random_selector.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-object-random-selector-") as directory:
        library = Path(directory) / "object-random-selector.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        select = recovered.recovered_object_state_random_selector
        select.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        select.restype = ctypes.c_uint32

        roles = (1, 1, 2, 2, 3, 3, 5, 6)
        vectors = 0
        for value in range(0x100000):
            role = ctypes.c_uint32(0xA5A5A5A5)
            assert select(value, ctypes.byref(role)) == 1
            assert role.value == roles[value & 7]
            vectors += 1

    print(f"recovered object-state random selector vectors: {vectors} ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
