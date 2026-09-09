#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("packed_byte_count", ctypes.c_uint32), ("initialized_halfword_count", ctypes.c_uint32),
        ("scan_record_count", ctypes.c_uint32), ("target_word", ctypes.c_uint32),
        ("workspace_base", ctypes.c_uint32), ("scan_base", ctypes.c_uint32),
        ("mismatch_558", ctypes.c_uint32), ("mismatch_55c", ctypes.c_uint32),
        ("mismatch_558_address", ctypes.c_uint32), ("mismatch_55c_address", ctypes.c_uint32),
        ("workspace_fill_value", ctypes.c_uint32), ("slot_558_address", ctypes.c_uint32),
        ("slot_55c_address", ctypes.c_uint32), ("return_target", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-alt-record-scan-") as d:
        so = Path(d) / "alt-record-scan.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_runtime_alternate_record_scan_eb450.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_runtime_alternate_record_scan_eb450
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint16),
                       ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        words = (ctypes.c_uint16 * 4)(0x9999, 0x1234, 0x1234, 0x8888)
        out = Result()
        assert fn(8, 0x1234, words, 4, ctypes.byref(out)) == 1
        assert (out.initialized_halfword_count, out.scan_record_count,
                out.workspace_base, out.scan_base, out.target_word) == (4, 2, 0x501cc0, 0x501cc8, 0x1234)
        assert (out.mismatch_558, out.mismatch_55c,
                out.mismatch_558_address, out.mismatch_55c_address) == (0x501cca, 0x501cd0, 0x501cca, 0x501cd0)
        assert (out.slot_558_address, out.slot_55c_address, out.workspace_fill_value,
                out.return_target) == (0x578558, 0x57855c, 0x1234, 0xeb508)
        assert fn(8, 0x1234, words, 3, ctypes.byref(out)) == 0
        print("PASS: 0xeb450 alternate packed-record scan")


if __name__ == "__main__":
    main()
