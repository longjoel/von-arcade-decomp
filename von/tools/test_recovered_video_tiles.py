#!/usr/bin/env python3
"""Exhaustively test the recovered indexed video-tile expanders."""

from __future__ import annotations

import ctypes
import os
import random
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_video_tiles.c"
TILE_WORDS = 256
PIXELS = 64


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-video-tiles-") as directory:
        library = Path(directory) / "video-tiles.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        prototypes = []
        for name in ("recovered_video_expand_tile", "recovered_video_expand_tile_mirrored"):
            function = getattr(recovered, name)
            function.argtypes = [
                ctypes.c_uint32,
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint16),
                ctypes.POINTER(ctypes.c_uint16),
                ctypes.POINTER(ctypes.c_uint16),
                ctypes.POINTER(ctypes.c_uint16),
            ]
            prototypes.append(function)

        indexed = recovered.recovered_video_expand_tile_indexed
        indexed.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_uint8)),
            ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(ctypes.c_uint16),
            ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(ctypes.c_uint16),
        ]

        generator = random.Random(0xE1F20)
        for tile in (0, 1, 7, 31):
            source_values = [generator.randrange(256) for _ in range(PIXELS * 3)]
            lookup_values = [generator.randrange(65536) for _ in range(256)]
            source = (ctypes.c_uint8 * len(source_values))(*source_values)
            lookup = (ctypes.c_uint16 * len(lookup_values))(*lookup_values)
            arrays = [(ctypes.c_uint16 * (TILE_WORDS * 32))(*([0xA55A] * (TILE_WORDS * 32))) for _ in range(3)]
            base = tile * TILE_WORDS

            prototypes[0](tile, source, lookup, *arrays)
            for pixel in range(PIXELS):
                for channel, array in enumerate(arrays):
                    expected = lookup_values[source_values[pixel * 3 + channel]]
                    if array[base + pixel] != expected:
                        raise SystemExit("unmirrored tile mismatch")
                    if array[base + 128 + pixel] != 0xA55A:
                        raise SystemExit("unmirrored tile wrote mirror half")

            arrays = [(ctypes.c_uint16 * (TILE_WORDS * 32))(*([0x5AA5] * (TILE_WORDS * 32))) for _ in range(3)]
            prototypes[1](tile, source, lookup, *arrays)
            for pixel in range(PIXELS):
                for channel, array in enumerate(arrays):
                    expected = lookup_values[source_values[pixel * 3 + channel]]
                    if array[base + pixel] != expected or array[base + 128 + pixel] != expected:
                        raise SystemExit("mirrored tile mismatch")

            other_values = [generator.randrange(256) for _ in range(PIXELS * 3)]
            other_source = (ctypes.c_uint8 * len(other_values))(*other_values)
            source_table = (ctypes.POINTER(ctypes.c_uint8) * 2)(source, other_source)
            arrays = [(ctypes.c_uint16 * (TILE_WORDS * 32))(*([0x5AA5] * (TILE_WORDS * 32))) for _ in range(3)]
            indexed(tile, 1, source_table, lookup, *arrays)
            for pixel in range(PIXELS):
                for channel, array in enumerate(arrays):
                    expected = lookup_values[other_values[pixel * 3 + channel]]
                    if array[base + pixel] != expected or array[base + 128 + pixel] != expected:
                        raise SystemExit("indexed tile mismatch")

    print("PASS: indexed 8x8 video-tile expansion and mirrored plane copies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
