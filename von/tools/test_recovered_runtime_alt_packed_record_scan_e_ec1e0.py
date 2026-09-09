#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "packed_byte_count", "initialized_halfword_count", "group_count",
        "records_per_group", "group_stride_bytes", "target_byte", "scan_base",
        "match_594", "slot_594_address", "return_target")]


def main():
    with tempfile.TemporaryDirectory(prefix="von-alt-packed-scan-e-") as d:
        so = Path(d) / "scan.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I",
                        str(ROOT / "von/i960"), "-o", str(so), str(ROOT /
                        "von/i960/recovered_runtime_alt_packed_record_scan_e_ec1e0.c")], check=True)
        fn = ctypes.CDLL(str(so)).recovered_runtime_alt_packed_record_scan_e_ec1e0
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint16),
                       ctypes.c_uint32, ctypes.POINTER(Result)]; fn.restype = ctypes.c_int
        words = (ctypes.c_uint16 * 4096)(); words[4095] = 0x0034
        out = Result()
        assert fn(0x4000, 0x34, words, 4096, ctypes.byref(out)) == 1
        assert (out.initialized_halfword_count, out.group_count, out.records_per_group,
                out.group_stride_bytes, out.scan_base, out.match_594,
                out.slot_594_address, out.return_target) == (
            0x2000, 32, 128, 0x200, 0x5785a4 + 0x4000,
            0x5785a4 + 0x4000 + 31 * 0x200 + 127 * 2, 0x578594, 0xec280)
        assert fn(0x4000, 0x34, words, 4095, ctypes.byref(out)) == 0
        print("PASS: 0xec1e0 strided alternate packed-record scan")


if __name__ == "__main__":
    main()
