#!/usr/bin/env python3
"""Exhaustively test the recovered video lookup-table producer."""

from __future__ import annotations

import ctypes
import os
import random
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_video_palette.c"
STEPS = [0xFA, 0xF5, 0xF0, 0xEB, 0xE6, 0xE6, 0xEB, 0xF0, 0xF5, 0xFA]
OFFSETS = [5, 10, 15, 20, 25, 40, 32, 24, 16, 8]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-video-palette-") as directory:
        library = Path(directory) / "video-palette.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        function = recovered.recovered_video_palette_lookup_initialize
        function.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint16,
            ctypes.POINTER(ctypes.c_uint16),
            ctypes.POINTER(ctypes.c_uint16),
            ctypes.POINTER(ctypes.c_uint16),
        ]
        function.restype = ctypes.c_uint16

        generator = random.Random(0xE1E08)
        selectors = list(range(0, 13))
        selectors.extend(generator.randrange(0x10000) for _ in range(1024))
        for selector in selectors:
            for initial in (0, 1, 0x1234, 0xFF00, 0xFFFF):
                lookup = (ctypes.c_uint16 * 256)()
                selected_step = ctypes.c_uint16(0xAAAA)
                stored_offset = ctypes.c_uint16(0xBBBB)
                actual_last = function(
                    selector, initial, lookup,
                    ctypes.byref(selected_step), ctypes.byref(stored_offset),
                )
                index = selector - 1
                if 0 <= index < 10:
                    step, offset = STEPS[index], OFFSETS[index]
                else:
                    step, offset = 0xFF, 0
                accumulator = 0
                for entry in range(256):
                    expected = (initial + offset + accumulator // 255) & 0xFFFF
                    if lookup[entry] != expected:
                        raise SystemExit(
                            f"lookup mismatch selector={selector} initial=0x{initial:04x} entry={entry}"
                        )
                    accumulator += step
                if actual_last != lookup[255] or selected_step.value != step or stored_offset.value != offset:
                    raise SystemExit("lookup metadata mismatch")

    print("PASS: 256-entry video lookup generation across all selectors and edge values")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
