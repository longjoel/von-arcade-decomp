#!/usr/bin/env python3
"""Exhaustively test the recovered text/tile control bus boundary."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-text-control-") as directory:
        library = Path(directory) / "text-control.so"
        subprocess.run(
            [
                os.environ.get("CC", "cc"),
                "-shared",
                "-fPIC",
                "-O2",
                SOURCE,
                "-o",
                library,
            ],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_text_tile_control_bus.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        recovered.recovered_text_tile_control_bus.restype = ctypes.c_uint32

        vectors = 0
        for value in range(0x10000):
            address = ctypes.c_uint32()
            actual = recovered.recovered_text_tile_control_bus(value, ctypes.byref(address))
            if actual != value or address.value != 0x01800000:
                raise SystemExit(
                    f"tile-control mismatch value=0x{value:04x}: "
                    f"address=0x{address.value:08x}, value=0x{actual:08x}"
                )
            vectors += 1

    print(f"PASS: {vectors:,} text/tile control vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
