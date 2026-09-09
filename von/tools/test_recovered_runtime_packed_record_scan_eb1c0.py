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
        ("target_low_byte", ctypes.c_uint32), ("target_high_byte", ctypes.c_uint32),
        ("workspace_base", ctypes.c_uint32), ("scan_base", ctypes.c_uint32),
        ("match_548", ctypes.c_uint32), ("match_54c", ctypes.c_uint32),
        ("match_550", ctypes.c_uint32), ("matched_548", ctypes.c_uint32),
        ("matched_54c", ctypes.c_uint32), ("matched_550", ctypes.c_uint32),
        ("match_548_address", ctypes.c_uint32), ("match_54c_address", ctypes.c_uint32),
        ("match_550_address", ctypes.c_uint32), ("workspace_fill_value", ctypes.c_uint32),
        ("slot_548_address", ctypes.c_uint32), ("slot_54c_address", ctypes.c_uint32),
        ("slot_550_address", ctypes.c_uint32), ("return_target", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-packed-record-scan-") as d:
        so = Path(d) / "packed-record-scan.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_runtime_packed_record_scan_eb1c0.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_runtime_packed_record_scan_eb1c0
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint16),
                       ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        words = (ctypes.c_uint16 * 4)(0x1200, 0x0034, 0x0034, 0x1200)
        out = Result()
        assert fn(8, 0x1234, words, 4, ctypes.byref(out)) == 1
        assert (out.initialized_halfword_count, out.scan_record_count,
                out.target_word, out.target_low_byte, out.target_high_byte,
                out.workspace_base, out.scan_base) == (4, 2, 0x1234, 0x34, 0x1200, 0x5785a4, 0x5785ac)
        assert (out.match_548, out.match_54c, out.match_550,
                out.match_548_address, out.match_54c_address,
                out.match_550_address) == (0x5785b0, 0x5785ae, 0x5785b2, 0x5785b0, 0x5785ae, 0x5785b2)
        assert (out.slot_548_address, out.slot_54c_address, out.slot_550_address,
                out.workspace_fill_value, out.return_target) == (0x578548, 0x57854c, 0x578550, 0x1234, 0xeb2bc)
        assert fn(8, 0x1234, words, 3, ctypes.byref(out)) == 0
        print("PASS: 0xeb1c0 packed-record scan")


if __name__ == "__main__":
    main()
