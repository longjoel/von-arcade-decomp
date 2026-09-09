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
        ("match_570", ctypes.c_uint32), ("match_574", ctypes.c_uint32),
        ("matched_570", ctypes.c_uint32), ("matched_574", ctypes.c_uint32),
        ("match_570_address", ctypes.c_uint32), ("match_574_address", ctypes.c_uint32),
        ("workspace_fill_value", ctypes.c_uint32), ("slot_570_address", ctypes.c_uint32),
        ("slot_574_address", ctypes.c_uint32), ("return_target", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-alt-packed-scan-") as d:
        so = Path(d) / "alt-packed-scan.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_runtime_alt_packed_record_scan_ebba0.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_runtime_alt_packed_record_scan_ebba0
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint16),
                       ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        words = (ctypes.c_uint16 * 3)(0x1234, 0x5600, 0x0034)
        out = Result()
        assert fn(6, 0x1234, words, 3, ctypes.byref(out)) == 1
        assert (out.initialized_halfword_count, out.scan_record_count,
                out.workspace_base, out.scan_base, out.target_low_byte,
                out.target_high_byte, out.workspace_fill_value,
                out.return_target) == (3, 3, 0x5785a4, 0x5785aa, 0x34, 0x1200, 0x1234, 0xebc5c)
        assert (out.match_570, out.match_574, out.match_570_address,
                out.match_574_address) == (0x5785ae, 0x5785aa, 0x5785ae, 0x5785aa)
        assert (out.slot_570_address, out.slot_574_address) == (0x578570, 0x578574)
        assert fn(6, 0x1234, words, 2, ctypes.byref(out)) == 0
        print("PASS: 0xebba0 alternate packed-record scan")


if __name__ == "__main__":
    main()
