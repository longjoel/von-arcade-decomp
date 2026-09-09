#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "packed_byte_count", "initialized_halfword_count", "scan_record_count",
        "target_word", "scan_base", "match_578", "match_57c", "match_580", "match_584",
        "slot_578_address", "slot_57c_address", "slot_580_address", "slot_584_address",
        "return_target")]


def main():
    with tempfile.TemporaryDirectory(prefix="von-alt-packed-scan-b-") as d:
        so = Path(d) / "scan.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I",
                        str(ROOT / "von/i960"), "-o", str(so), str(ROOT /
                        "von/i960/recovered_runtime_alt_packed_record_scan_b_ebd20.c")], check=True)
        fn = ctypes.CDLL(str(so)).recovered_runtime_alt_packed_record_scan_b_ebd20
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint16),
                       ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        words = (ctypes.c_uint16 * 4)(0x1234, 0x5600, 0x0034, 0x1200)
        out = Result()
        assert fn(8, 0x1234, words, 4, ctypes.byref(out)) == 1
        assert (out.initialized_halfword_count, out.scan_record_count, out.scan_base,
                out.match_578, out.match_57c, out.match_580, out.match_584,
                out.return_target) == (4, 2, 0x5785ac, 0x5785b0, 0x5785ac,
                                       0x0, 0x5785b2, 0xebe1c)
        assert fn(8, 0x1234, words, 3, ctypes.byref(out)) == 0
        print("PASS: 0xebd20 paired alternate packed-record scan")


if __name__ == "__main__":
    main()
