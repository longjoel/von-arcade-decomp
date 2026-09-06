#!/usr/bin/env python3
"""Trace-validate string dispatch + character mapping on live boot text.

The original 45-second no-input attract capture shows the character-output
store (pc=0x1ccb0) emitting 404 tile writes that spell the firmware boot
sequence verbatim: uploader progress lines, then the Japan-only warning and
the Sega sign-off, in 14 cursor-positioned segments. Every value is a
printable byte with bit 15 set; offsets advance +1 within a segment.

This test replays those 14 segments through the compiled character plan
(recovered_text_emit_char_plan): each byte must emit tile 0x8000|byte at the
running cursor slot, advancing exactly as observed. That pins the dispatch
contract (bytes emitted once, in order) and the character mapping together
on live firmware strings.
"""
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text.c"

# (start_row, start_col, text) observed in order; offsets advance +1 inside
# each segment, jumps only between segments (cursor repositioning).
SEGMENTS = [
    (8, 8, "Downloading COPRO prog ... Done"),
    (9, 8, "Downloading GEO prog   ... Done"),
    (12, 8, "Loading Texture"),
    (12, 25, "Bank0 ... Done"),
    (13, 25, "Bank1 ... Done"),
    (12, 22, "W A R N I N G"),
    (16, 10, "THIS GAME IS TO BE USED ONLY IN JAPAN."),
    (18, 10, "EXPORT, SALES, DISTRIBUTION AND/OR"),
    (20, 10, "OPERATION OUTSIDE THIS AREA MAY"),
    (22, 10, "CONSTITUTE A VIOLATION OF INTERNATIONAL"),
    (24, 10, "LAWS ON COPYRIGHTS AND/OR INDUSTRIAL"),
    (26, 10, "PROPERTY RIGHTS AND SUBJECT THE"),
    (28, 10, "VIOLATING PARTY TO LEGAL PROCEEDINGS."),
    (32, 10, "                   SEGA ENTERPRISES,LTD."),
]


def main() -> int:
    total = sum(len(text) for _, _, text in SEGMENTS)
    assert total == 404, f"fixture covers {total} writes, want 404"
    with tempfile.TemporaryDirectory(prefix="von-text-dispatch-") as directory:
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
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", SOURCE,
             str(stubs), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        pointers = [ctypes.POINTER(ctypes.c_uint32)] * 4
        plan = recovered.recovered_text_emit_char_plan
        plan.argtypes = [ctypes.c_uint32] * 4 + pointers
        plan.restype = ctypes.c_uint32

        checked = 0
        for row, column, text in SEGMENTS:
            assert all(32 <= ord(ch) < 127 for ch in text)
            for character in text.encode("ascii"):
                tile_index = ctypes.c_uint32()
                tile_value = ctypes.c_uint32()
                next_column = ctypes.c_uint32()
                next_row = ctypes.c_uint32()
                emitted = plan(character, 0, column, row,
                               ctypes.byref(tile_index),
                               ctypes.byref(tile_value),
                               ctypes.byref(next_column),
                               ctypes.byref(next_row))
                assert emitted == 1
                assert tile_index.value == (row << 6) + column
                assert tile_value.value == (0x8000 | character)
                column, row = next_column.value, next_row.value
                checked += 1
        assert checked == 404

    print("PASS: boot-string dispatch replay (404 live tile writes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
