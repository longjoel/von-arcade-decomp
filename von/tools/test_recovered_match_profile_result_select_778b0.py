#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Candidate(ctypes.Structure):
    _fields_ = [
        ("table_word0", ctypes.c_int16),
        ("table_word2", ctypes.c_int16),
        ("table_word4", ctypes.c_int16),
        ("wrapped_gate_value", ctypes.c_uint16),
        ("returned_metric", ctypes.c_int32),
    ]


class Selection(ctypes.Structure):
    _fields_ = [
        ("selected_index", ctypes.c_uint32),
        ("selected_metric", ctypes.c_int32),
        ("scanned_count", ctypes.c_uint32),
        ("table_base", ctypes.c_uint32),
        ("table_stride", ctypes.c_uint32),
        ("gate_limit", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-profile-select-") as d:
        so = Path(d) / "profile-select.so"
        subprocess.run([
            os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
            "-o", str(so),
            str(ROOT / "von/i960/recovered_match_profile_result_select_778b0.c"),
        ], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_match_profile_result_select_778b0
        fn.argtypes = [ctypes.POINTER(Candidate)]
        fn.restype = Selection
        values = (Candidate * 8)()
        for i in range(8):
            values[i] = Candidate(i + 1, i + 2, 1, 0x100 + i, 100 - i)
        values[1].table_word4 = 0
        values[2].wrapped_gate_value = 0x7fff
        values[5].returned_metric = 10
        values[6].returned_metric = 10
        out = fn(values)
        assert (out.selected_index, out.selected_metric, out.scanned_count,
                out.table_base, out.table_stride, out.gate_limit) == \
            (5, 10, 8, 0x505060, 6, 0x7ffe)
        for i in range(8):
            values[i].table_word4 = 0
        out = fn(values)
        assert out.selected_index == 0xffffffff
        print("PASS: 0x778b0 eight-record gate and strict-minimum selection")


if __name__ == "__main__":
    main()
