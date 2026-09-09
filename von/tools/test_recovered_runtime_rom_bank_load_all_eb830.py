#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("selector_entry", ctypes.c_uint32), ("loader_count", ctypes.c_uint32),
        ("loader_entry", ctypes.c_uint32 * 8), ("mismatch_slot_address", ctypes.c_uint32 * 2),
        ("normalized_mismatch_value", ctypes.c_uint32),
        ("mismatch_558_before", ctypes.c_uint32), ("mismatch_55c_before", ctypes.c_uint32),
        ("mismatch_558_after", ctypes.c_uint32), ("mismatch_55c_after", ctypes.c_uint32),
        ("status_counter_before", ctypes.c_uint32), ("status_counter_after", ctypes.c_uint32),
        ("status_counter_address", ctypes.c_uint32), ("return_target", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-rom-bank-all-") as d:
        so = Path(d) / "rom-bank-all.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_runtime_rom_bank_load_all_eb830.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_runtime_rom_bank_load_all_eb830
        fn.argtypes = [ctypes.c_uint32] * 3
        fn.restype = Result
        out = fn(0, 0x1234, 7)
        assert (out.selector_entry, out.loader_count, out.normalized_mismatch_value,
                out.mismatch_558_after, out.mismatch_55c_after,
                out.status_counter_after, out.status_counter_address,
                out.return_target) == (0xeb3b8, 8, 1, 1, 0x1234, 8, 0x578510, 0xeb898)
        assert list(out.loader_entry) == [0xeb5b0, 0xeb600, 0xeb650, 0xeb6a0,
                                          0xeb6f0, 0xeb740, 0xeb790, 0xeb7e0]
        assert list(out.mismatch_slot_address) == [0x578558, 0x57855c]
        print("PASS: 0xeb830 ROM-bank orchestrator")


if __name__ == "__main__":
    main()
