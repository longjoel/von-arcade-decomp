#!/usr/bin/env python3
"""Check the 0x1d6a0 glyph-writer normalization and tile schedule."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_glyph_writer_1d6a0.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-glyph-writer-") as directory:
        library = Path(directory) / "glyph-writer.so"
        subprocess.run([
            os.environ.get("CC", "cc"), "-shared", "-fPIC", str(SOURCE),
            "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))
        plan = recovered.recovered_text_glyph_writer_1d6a0_plan
        plan.argtypes = [ctypes.c_uint32] * 5 + [
            ctypes.POINTER(ctypes.c_uint32)] * 4
        plan.restype = ctypes.c_uint32
        vectors = 0
        for character in (0x21, 0x00, 0x20, 0x41, 0x7c, 0xfc):
            for column in (0, 60, 61, 62):
                normalized = ctypes.c_uint32()
                next_column = ctypes.c_uint32()
                next_row = ctypes.c_uint32()
                is_control = ctypes.c_uint32()
                result = plan(character, 3, column, 8, 2,
                              ctypes.byref(normalized), ctypes.byref(next_column),
                              ctypes.byref(next_row), ctypes.byref(is_control))
                if result != 1:
                    raise SystemExit("glyph writer plan failed")
                if character == 0x21:
                    expected = (0, 3, 9, 1)
                else:
                    index = (character & 0x7f)
                    index = 0 if index < 0x20 else index - 0x20
                    adjusted = column + (1 if index == 0x5c else 0)
                    expected = (index, adjusted + 2 if adjusted <= 61 else adjusted,
                                8, 0)
                if (normalized.value, next_column.value, next_row.value,
                        is_control.value) != expected:
                    raise SystemExit("glyph writer cursor mismatch")
                vectors += 1

        tile = recovered.recovered_text_glyph_writer_1d6a0_tile_plan
        tile.argtypes = [ctypes.c_uint32] * 7 + [
            ctypes.POINTER(ctypes.c_uint32)] * 3
        tile.restype = ctypes.c_uint32
        for plane in (0, 1, 2):
            for entry in (0, 1, 3, 4):
                source_address = ctypes.c_uint32()
                tile_address = ctypes.c_uint32()
                tile_value = ctypes.c_uint32()
                result = tile(8, 5, 4, plane, entry, 0x02ea11d0, 0x1234,
                              ctypes.byref(source_address), ctypes.byref(tile_address),
                              ctypes.byref(tile_value))
                valid = plane < 2 and entry < 4
                if result != int(valid):
                    raise SystemExit("glyph writer tile validity mismatch")
                if valid:
                    if (source_address.value != 0x02ea11d0 + ((plane * 4 + entry) << 1)
                            or tile_address.value != 0x01000000
                            + (((8 + plane) * 64 + 5 + entry) << 1)
                            or tile_value.value != 0x9234):
                        raise SystemExit("glyph writer tile mismatch")

    print(f"PASS: {vectors} 0x1d6a0 cursor vectors and tile schedule")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
