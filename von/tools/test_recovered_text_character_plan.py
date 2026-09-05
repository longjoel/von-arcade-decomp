#!/usr/bin/env python3
"""Contract test for printable, TAB, LF, and control-character text plans."""

from pathlib import Path
import ctypes
import os
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-text-character-") as directory:
        directory = Path(directory)
        stubs = directory / "stubs.c"
        stubs.write_text(
            "typedef unsigned int u32; typedef unsigned short u16; "
            "typedef unsigned char u8;\n"
            "void recovered_memory_copy_forward(volatile u8 *a, "
            "volatile const u8 *b, u32 c) { (void)a; (void)b; (void)c; }\n"
            "void recovered_host_fatal_halt(void) {}\n",
            encoding="utf-8",
        )
        library = directory / "text.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", str(SOURCE),
             str(stubs), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        pointers = [ctypes.POINTER(ctypes.c_uint32)] * 4
        recovered.recovered_text_emit_char_plan.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            *pointers]
        recovered.recovered_text_emit_char_plan.restype = ctypes.c_uint32

        vectors = 0
        for character in range(256):
            for column in (0, 1, 7, 8, 61, 62, 63):
                for row in (0, 46, 47):
                    origin, tile_index = 3, ctypes.c_uint32()
                    tile_value = ctypes.c_uint32()
                    next_column = ctypes.c_uint32()
                    next_row = ctypes.c_uint32()
                    emitted = recovered.recovered_text_emit_char_plan(
                        character, origin, column, row,
                        ctypes.byref(tile_index), ctypes.byref(tile_value),
                        ctypes.byref(next_column), ctypes.byref(next_row))
                    if character > 31:
                        if emitted != 1 or tile_index.value != (row << 6) + column:
                            raise SystemExit("printable tile plan mismatch")
                        if tile_value.value != (0x8000 | character):
                            raise SystemExit("printable tile value mismatch")
                        expected_column = column + 1 if column <= 61 else column
                        expected_row = row
                    elif character == 9:
                        if emitted != 0 or tile_value.value != 0:
                            raise SystemExit("TAB plan emitted a tile")
                        tab_column = (column + 8) & ~7
                        expected_column = tab_column if tab_column <= 61 else 0
                        expected_row = row + 1 if tab_column > 61 and row <= 46 else row
                    elif character == 10:
                        if emitted != 0 or tile_value.value != 0:
                            raise SystemExit("LF plan emitted a tile")
                        expected_column = origin
                        expected_row = row + 1 if row <= 46 else row
                    else:
                        if emitted != 0 or tile_value.value != 0:
                            raise SystemExit("control plan emitted a tile")
                        expected_column, expected_row = column, row
                    if (next_column.value, next_row.value) != (expected_column, expected_row):
                        raise SystemExit("text state transition mismatch")
                    vectors += 1

    print(f"PASS: {vectors:,} text-character transition vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
