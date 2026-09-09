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
        ("first_target", ctypes.c_uint32), ("power_target_first", ctypes.c_uint32),
        ("power_target_last", ctypes.c_uint32), ("caller_target", ctypes.c_uint32),
        ("scan_call_count", ctypes.c_uint32), ("scan_target", ctypes.c_uint32 * 18),
        ("match_slot_address", ctypes.c_uint32 * 4), ("normalized_match_value", ctypes.c_uint32),
        ("status_counter_before", ctypes.c_uint32), ("status_counter_after", ctypes.c_uint32),
        ("scanner_address", ctypes.c_uint32), ("return_target", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-record-init-") as d:
        so = Path(d) / "record-init.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_runtime_record_table_init_eb2c0.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_runtime_record_table_init_eb2c0
        fn.argtypes = [ctypes.c_uint32] * 2
        fn.restype = Result
        out = fn(0x55, 9)
        assert (out.workspace_base, out.packed_byte_count, out.first_target,
                out.power_target_first, out.power_target_last, out.caller_target,
                out.scan_call_count) == (0x200000, 0x220000, 0xffff, 1, 0x8000, 0x55, 18)
        assert list(out.scan_target) == [0xffff] + [1 << i for i in range(16)] + [0x55]
        assert list(out.match_slot_address) == [0x578548, 0x57854c, 0x578550, 0x578554]
        assert (out.normalized_match_value, out.status_counter_after,
                out.scanner_address, out.return_target) == (1, 10, 0xeb1c0, 0xeb3a4)
        print("PASS: 0xeb2c0 packed-record table initializer")


if __name__ == "__main__":
    main()
