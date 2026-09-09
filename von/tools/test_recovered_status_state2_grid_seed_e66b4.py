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
                ("source_count", ctypes.c_uint32),
                ("frame_record_stride", ctypes.c_uint32),
                ("frame_word40_offset", ctypes.c_uint32),
                ("frame_word44_offset", ctypes.c_uint32),
                ("initial_word40", ctypes.c_uint32),
                ("initial_word44", ctypes.c_uint32),
                ("source_sum", ctypes.c_int32),
                ("normalized_sum", ctypes.c_int32),
                ("next_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-state2-grid-seed-") as d:
        so = Path(d) / "status-state2-grid-seed.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_state2_grid_seed_e66b4.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_state2_grid_seed_e66b4
        fn.argtypes = [ctypes.c_int32]
        fn.restype = Result
        out = fn(12)
        assert (out.source_base, out.source_stride, out.source_count,
                out.frame_record_stride, out.frame_word40_offset,
                out.frame_word44_offset, out.initial_word40, out.initial_word44,
                out.source_sum, out.normalized_sum, out.next_target) == \
            (0x1d000a4, 16, 10, 12, 0x40, 0x44, 0xffffffff, 0, 12, 12,
             0xe6708)
        assert fn(0).normalized_sum == 1
        assert fn(-3).normalized_sum == 1
        print("PASS: 0xe66b4 state-2 grid seed phase")


if __name__ == "__main__":
    main()
