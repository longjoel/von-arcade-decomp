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
        recovered.recovered_text_string_font_mode.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
        ]
        recovered.recovered_text_string_font_mode.restype = ctypes.c_uint32

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

        mode_vectors = 0
        for first in range(0x100):
            for second in range(0x100):
                text = (ctypes.c_ubyte * 3)(first, second, 0)
                expected = 0 if first != 0 and 0x61 <= second <= 0x7A else 1
                actual = recovered.recovered_text_string_font_mode(text)
                if actual != expected:
                    raise SystemExit(
                        f"font-mode mismatch first=0x{first:02x} "
                        f"second=0x{second:02x}: {actual} != {expected}"
                    )
                mode_vectors += 1

    print(
        f"PASS: {vectors:,} text/tile control vectors and "
        f"{mode_vectors:,} font-mode prefixes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
