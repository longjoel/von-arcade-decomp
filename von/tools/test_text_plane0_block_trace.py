#!/usr/bin/env python3
"""Trace-validate the 0x1dc10 plane-0 block writer against the attract burst.

The original 45-second no-input attract capture shows the writer's inner
store (pc=0x1dc68) emitting 1920 tile writes covering plane-0 slots 0..1919
exactly once (offsets strictly +1, no gaps), background value 0xb480 with
617 content writes clustered in glyph runs (first at 0x108), every value
carrying bit 15. That footprint is a complete 64x30 tile region, whether one
64x30 call or row-joined smaller calls -- the stream cannot distinguish, so
the call split stays unresolved.

This test replays that exact 64x30 region through the compiled cell-plan
model: all 1920 cells must validate, land on slots 0..1919 exactly once,
and map source word 0x3480 to the observed background 0xb480.
"""
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_plane0_block.c"

# Recorded aggregate properties of the pc=0x1dc68 burst (see module docstring).
BURST_START = 0
BURST_COUNT = 1920
BURST_BACKGROUND = 0xB480
BURST_SOURCE_WORD = 0x3480
REGION_WIDTH = 64
REGION_HEIGHT = 30


class Cell(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source_byte_offset", "destination_byte_address", "source_word_or_mask")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-plane0-trace-") as directory:
        library = Path(directory) / "plane0-block.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_text_plane0_cell_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.POINTER(Cell)]
        plan_fn.restype = ctypes.c_uint32

        seen = set()
        cell = Cell()
        for y in range(REGION_HEIGHT):
            for x in range(REGION_WIDTH):
                assert plan_fn(0, 0, REGION_WIDTH, REGION_HEIGHT,
                               y, x, BURST_SOURCE_WORD, ctypes.byref(cell)) == 1
                slot = (cell.destination_byte_address - 0x01000000) // 2
                assert slot == y * 64 + x, f"cell {(y, x)} maps off-grid"
                assert cell.source_word_or_mask == BURST_BACKGROUND
                assert cell.source_byte_offset == ((y * REGION_WIDTH) + x) << 1
                seen.add(slot)
        assert seen == set(range(BURST_COUNT)), "model footprint != burst footprint"
        assert BURST_START == 0 and BURST_COUNT == REGION_WIDTH * REGION_HEIGHT

        # Out-of-region cells are rejected, so content outside 64x30 could
        # never come from this plan shape.
        assert plan_fn(0, 0, REGION_WIDTH, REGION_HEIGHT,
                       REGION_HEIGHT, 0, 0, ctypes.byref(cell)) == 0

    print("PASS: 0x1dc10 plane-0 block trace replay (1920-cell region)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
