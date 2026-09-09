#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("source_base", ctypes.c_uint32),
                ("source_stride", ctypes.c_uint32),
                ("row_count", ctypes.c_uint32),
                ("column_count", ctypes.c_uint32),
                ("frame_record_stride", ctypes.c_uint32),
                ("frame_word40_offset", ctypes.c_uint32),
                ("frame_word44_offset", ctypes.c_uint32),
                ("frame_word48_offset", ctypes.c_uint32),
                ("percentage_scale", ctypes.c_uint32),
                ("next_row_target", ctypes.c_uint32),
                ("after_rows_target", ctypes.c_uint32),
                ("source_value", ctypes.c_int32),
                ("normalized_sum", ctypes.c_int32),
                ("percentage", ctypes.c_int32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-state2-grid-match-") as d:
        so = Path(d) / "status-state2-grid-match.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_state2_grid_match_e6708.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_state2_grid_match_e6708
        fn.argtypes = [ctypes.c_int32, ctypes.c_int32]
        fn.restype = Result
        out = fn(25, 100)
        assert (out.source_base, out.source_stride, out.row_count,
                out.column_count, out.frame_record_stride, out.frame_word40_offset,
                out.frame_word44_offset, out.frame_word48_offset,
                out.percentage_scale, out.next_row_target, out.after_rows_target,
                out.source_value, out.normalized_sum, out.percentage) == \
            (0x1d000a4, 16, 8, 8, 12, 0x40, 0x44, 0x48, 100, 0xe6714,
             0xe67f4, 25, 100, 25)
        assert fn(10, 0).percentage == 0
        assert fn(-25, 100).percentage == -25
        print("PASS: 0xe6708 state-2 grid matching pass")


if __name__ == "__main__":
    main()
