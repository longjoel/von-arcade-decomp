#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("primary_match", ctypes.c_uint32 * 4), ("alternate_match", ctypes.c_uint32 * 4),
        ("primary_all_one", ctypes.c_uint32), ("alternate_all_one", ctypes.c_uint32),
        ("selected_base", ctypes.c_uint32), ("selected_family", ctypes.c_uint32),
        ("publication_address", ctypes.c_uint32), ("continuation_target", ctypes.c_uint32),
        ("primary_base", ctypes.c_uint32), ("alternate_base", ctypes.c_uint32),
        ("fallback_base", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-record-base-") as d:
        so = Path(d) / "record-base.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_runtime_record_base_select_eb3b0.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_runtime_record_base_select_eb3b0
        fn.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
        fn.restype = Result
        cases = [([1, 1, 1, 1], [0, 0, 0, 0], 0x200000, 0),
                 ([1, 1, 0, 1], [1, 1, 1, 1], 0x1080000, 1),
                 ([1, 1, 0, 1], [1, 0, 1, 1], 0x5e0000, 2)]
        for primary, alternate, expected_base, expected_family in cases:
            p = (ctypes.c_uint32 * 4)(*primary)
            a = (ctypes.c_uint32 * 4)(*alternate)
            out = fn(p, a, 0x123456)
            assert (out.selected_base, out.selected_family, out.publication_address,
                    out.continuation_target, out.primary_all_one, out.alternate_all_one) == (
                expected_base, expected_family, 0x501cc4, 0x123456,
                int(primary == [1, 1, 1, 1]), int(alternate == [1, 1, 1, 1]))
        print("PASS: 0xeb3b0 runtime record base selector")


if __name__ == "__main__":
    main()
