#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("row_count", ctypes.c_uint32),
                ("frame_record_stride", ctypes.c_uint32),
                ("frame_word40_offset", ctypes.c_uint32),
                ("frame_word48_offset", ctypes.c_uint32),
                ("first_text_column", ctypes.c_uint32),
                ("text_column_stride", ctypes.c_uint32),
                ("even_formatter", ctypes.c_uint32),
                ("odd_formatter", ctypes.c_uint32),
                ("even_helper_argument", ctypes.c_uint32),
                ("odd_helper_argument", ctypes.c_uint32),
                ("formatter_target", ctypes.c_uint32),
                ("lookup_target", ctypes.c_uint32),
                ("numeric_target", ctypes.c_uint32),
                ("suffix_target", ctypes.c_uint32),
                ("suffix_formatter_target", ctypes.c_uint32),
                ("row_formatter", ctypes.c_uint32 * 4),
                ("row_helper_argument", ctypes.c_uint32 * 4),
                ("row_frame_offset", ctypes.c_uint32 * 4),
                ("row_text_column", ctypes.c_uint32 * 4),
                ("next_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-state2-row-render-") as d:
        so = Path(d) / "status-state2-row-render.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_state2_grid_row_render_e6818.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_state2_grid_row_render_e6818
        fn.restype = Result
        out = fn()
        assert (out.row_count, out.frame_record_stride, out.frame_word40_offset,
                out.frame_word48_offset, out.first_text_column,
                out.text_column_stride, out.even_formatter, out.odd_formatter,
                out.even_helper_argument, out.odd_helper_argument,
                out.formatter_target, out.lookup_target, out.numeric_target,
                out.suffix_target, out.suffix_formatter_target,
                list(out.row_formatter), list(out.row_helper_argument),
                list(out.row_frame_offset), list(out.row_text_column),
                out.next_target) == \
            (4, 12, 0x40, 0x48, 19, 3, 8, 16, 13, 21, 0x1cac8,
             0xe3a00, 0xe3a60, 0xe665c, 0x1d9e0, [8, 16, 8, 16],
             [13, 21, 13, 21], [0, 12, 24, 36], [19, 22, 25, 28],
             0xe6930)
        print("PASS: 0xe6818 state-2 row rendering plan")


if __name__ == "__main__":
    main()
