#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("current_row", ctypes.c_uint32),
                ("next_row", ctypes.c_uint32),
                ("continue_loop", ctypes.c_uint32),
                ("current_record_offset", ctypes.c_uint32),
                ("next_record_offset", ctypes.c_uint32),
                ("current_text_column", ctypes.c_uint32),
                ("next_text_column", ctypes.c_uint32),
                ("record_base", ctypes.c_uint32),
                ("record_stride", ctypes.c_uint32),
                ("text_column_increment", ctypes.c_uint32),
                ("loop_limit", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-row-") as d:
        so = Path(d) / "status-row.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_render_row_advance_e5ebc.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_render_row_advance_e5ebc
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        fn.restype = Result
        first = fn(0, 0, 19)
        assert (first.next_row, first.continue_loop, first.next_record_offset,
                first.next_text_column, first.continuation) == (1, 1, 8, 22, 0xe5e20)
        last = fn(4, 32, 31)
        assert (last.next_row, last.continue_loop, last.next_record_offset,
                last.next_text_column, last.continuation) == (5, 0, 40, 34, 0xe60d0)
        assert (last.record_base, last.record_stride,
                last.text_column_increment, last.loop_limit) == (0x578410, 8, 3, 4)
        print("PASS: 0xe5ebc status-render row advance")


if __name__ == "__main__":
    main()
