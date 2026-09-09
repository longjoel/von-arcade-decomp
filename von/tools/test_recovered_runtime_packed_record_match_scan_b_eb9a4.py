#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("packed_byte_count", ctypes.c_uint32), ("initialized_dword_count", ctypes.c_uint32),
        ("scan_record_count", ctypes.c_uint32), ("target_word", ctypes.c_uint32),
        ("workspace_base", ctypes.c_uint32), ("scan_base", ctypes.c_uint32),
        ("byte_mask", ctypes.c_uint32 * 4), ("match_address", ctypes.c_uint32 * 4),
        ("matched", ctypes.c_uint32 * 4), ("slot_address", ctypes.c_uint32 * 4),
        ("workspace_fill_value", ctypes.c_uint32), ("return_target", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-record-match-scan-b-") as d:
        so = Path(d) / "record-match-scan-b.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_runtime_packed_record_match_scan_b_eb9a4.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_runtime_packed_record_match_scan_b_eb9a4
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                       ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        words = (ctypes.c_uint32 * 1)(0x12345678)
        out = Result()
        assert fn(4, 0x12345678, words, 1, ctypes.byref(out)) == 1
        assert (out.initialized_dword_count, out.scan_record_count,
                out.workspace_base, out.scan_base, out.return_target) == (1, 1, 0x910004, 0x910008, 0xebaa4)
        assert list(out.match_address) == [0x910008, 0x910008, 0x910008, 0x910008]
        assert list(out.slot_address) == [0x578560, 0x578564, 0x578568, 0x57856c]
        assert fn(4, 0x12345678, words, 0, ctypes.byref(out)) == 0
        print("PASS: 0xeb9a4 second packed-record match scan")


if __name__ == "__main__":
    main()
