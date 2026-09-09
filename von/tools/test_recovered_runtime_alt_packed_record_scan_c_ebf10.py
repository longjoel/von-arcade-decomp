#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "packed_byte_count", "initialized_halfword_count", "scan_record_count",
        "target_word", "scan_base", "match_588", "match_58c",
        "slot_588_address", "slot_58c_address", "return_target")]


def main():
    with tempfile.TemporaryDirectory(prefix="von-alt-packed-scan-c-") as d:
        so = Path(d) / "scan.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I",
                        str(ROOT / "von/i960"), "-o", str(so), str(ROOT /
                        "von/i960/recovered_runtime_alt_packed_record_scan_c_ebf10.c")], check=True)
        fn = ctypes.CDLL(str(so)).recovered_runtime_alt_packed_record_scan_c_ebf10
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint16),
                       ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        words = (ctypes.c_uint16 * 3)(0x1234, 0x5600, 0x1200)
        out = Result()
        assert fn(6, 0x1234, words, 3, ctypes.byref(out)) == 1
        assert (out.initialized_halfword_count, out.scan_record_count, out.scan_base,
                out.match_588, out.match_58c, out.slot_588_address,
                out.slot_58c_address, out.return_target) == (
            3, 3, 0x5785aa, 0x5785aa, 0x5785ae, 0x578588, 0x57858c, 0xebfcc)
        assert fn(6, 0x1234, words, 2, ctypes.byref(out)) == 0
        print("PASS: 0xebf10 alternate packed-record scan")


if __name__ == "__main__":
    main()
