#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("workspace_base", ctypes.c_uint32), ("packed_byte_count", ctypes.c_uint32),
        ("first_target", ctypes.c_uint32), ("shifted_target_first", ctypes.c_uint32),
        ("shifted_target_last", ctypes.c_uint32), ("caller_target", ctypes.c_uint32),
        ("scan_call_count", ctypes.c_uint32), ("scan_target", ctypes.c_uint32 * 18),
        ("scanner_address", ctypes.c_uint32), ("match_slot_address", ctypes.c_uint32 * 2),
        ("normalized_match_value", ctypes.c_uint32),
        ("status_counter_before", ctypes.c_uint32), ("status_counter_after", ctypes.c_uint32),
        ("status_counter_address", ctypes.c_uint32), ("return_target", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-alt-record-init-ebc60-") as d:
        so = Path(d) / "alt-record-init-ebc60.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_runtime_alt_record_table_init_ebc60.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_runtime_alt_record_table_init_ebc60
        fn.argtypes = [ctypes.c_uint32] * 2
        fn.restype = Result
        out = fn(0x12345678, 9)
        assert (out.workspace_base, out.packed_byte_count, out.first_target,
                out.shifted_target_first, out.shifted_target_last, out.scan_call_count,
                out.scanner_address, out.normalized_match_value,
                out.status_counter_after, out.status_counter_address,
                out.return_target) == (
            0x1000000, 0x10000, 0xffff, 1, 0x8000, 18, 0xebba0, 1, 10,
            0x578510, 0xebd14)
        assert list(out.scan_target) == [0xffff] + [1 << i for i in range(16)] + [0x12345678]
        assert list(out.match_slot_address) == [0x578570, 0x578574]
        print("PASS: 0xebc60 alternate record initializer")


if __name__ == "__main__":
    main()
