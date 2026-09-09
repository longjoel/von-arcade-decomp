#!/usr/bin/env python3
"""Test the 0x1d570 status-glyph normalization and source selection."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_status_glyph.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("glyph_index", "source_kind", "source", "descriptor", "rows", "adjustment")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-glyph-") as directory:
        library = Path(directory) / "status-glyph.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_text_status_glyph_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Plan)]
        plan = Plan()
        adjustment = ctypes.c_uint32(1)

        plan_fn(0x61, ctypes.byref(adjustment), ctypes.byref(plan))
        assert (plan.glyph_index, plan.source_kind, plan.source, plan.descriptor, plan.rows, plan.adjustment) == (65, 0, 0, 0x02EA16D8, 2, 1)
        plan_fn(0x49, None, ctypes.byref(plan))
        assert (plan.glyph_index, plan.source_kind, plan.source) == (41, 1, 0x02FD7C90)
        plan_fn(0x4A, None, ctypes.byref(plan))
        assert (plan.glyph_index, plan.source_kind, plan.source) == (42, 1, 0x02FD7C98)
        plan_fn(0x00, None, ctypes.byref(plan))
        assert plan.glyph_index == 0
        plan_fn(0xFF, None, ctypes.byref(plan))
        assert plan.glyph_index == 95

        tile_fn = recovered.recovered_text_status_glyph_tile_plan
        tile_fn.argtypes = [ctypes.c_uint32] * 7 + [
            ctypes.POINTER(ctypes.c_uint32)] * 3
        tile_fn.restype = ctypes.c_uint32
        checked = 0
        for width in (1, 2, 4, 19):
            for plane in (0, 1, 2):
                for entry in (0, 1, width - 1, width):
                    source_address = ctypes.c_uint32()
                    tile_address = ctypes.c_uint32()
                    tile_value = ctypes.c_uint32()
                    result = tile_fn(
                        5, 7, width, plane, entry, 0x02fd7c90,
                        0x1234, ctypes.byref(source_address),
                        ctypes.byref(tile_address), ctypes.byref(tile_value))
                    valid = plane < 2 and entry < width
                    if result != int(valid):
                        raise SystemExit("status glyph tile validity mismatch")
                    if valid:
                        expected_source = 0x02fd7c90 + ((plane * width + entry) << 1)
                        expected_tile = 0x01000000 + (((5 + plane) * 64 + 7 + entry) << 1)
                        if (source_address.value, tile_address.value, tile_value.value) != (
                                expected_source, expected_tile, 0x9234):
                            raise SystemExit("status glyph tile schedule mismatch")
                        checked += 1

        next_fn = recovered.recovered_text_status_glyph_next_column
        next_fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(ctypes.c_uint32)]
        next_fn.restype = ctypes.c_uint32
        for character in (0x00, 0x29, 0x2a, 0x2b, 0x61, 0x7f, 0xff):
            for column in (0, 60, 61, 62):
                for width, trailing_flag in ((1, 0), (2, 1), (4, 1)):
                    next_column = ctypes.c_uint32()
                    result = next_fn(character, column, width, trailing_flag,
                                     ctypes.byref(next_column))
                    normalized = character & 0x7f
                    if normalized < 0x20:
                        normalized = 0
                    expected = column
                    if trailing_flag == 1 and ((normalized + 0xd7) & 0xff) > 1:
                        expected += 1
                    if expected <= 61:
                        expected += width
                    if result != 1 or next_column.value != expected:
                        raise SystemExit("status glyph cursor tail mismatch")

    print(f"PASS: 0x1d570 status-glyph selector, {checked} tile vectors, and cursor tails")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
