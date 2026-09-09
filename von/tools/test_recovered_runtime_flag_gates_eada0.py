#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("variant", ctypes.c_uint32), ("entry_address", ctypes.c_uint32),
        ("flag_address", ctypes.c_uint32), ("fallback_address", ctypes.c_uint32),
        ("flag_bit_mask", ctypes.c_uint32), ("fallback_bit_mask", ctypes.c_uint32),
        ("flag_byte", ctypes.c_uint32), ("fallback_word", ctypes.c_uint32),
        ("accepted", ctypes.c_uint32), ("returned_value", ctypes.c_uint32),
        ("continuation_target", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-runtime-flags-") as d:
        so = Path(d) / "runtime-flags.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_runtime_flag_gates_eada0.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_runtime_flag_gates_eada0
        fn.argtypes = [ctypes.c_uint32] * 4
        fn.restype = Result
        expected = [
            (0xeada0, 0x5023f0, 0x5024b4, 0x08, 0x02),
            (0xeade0, 0x5023f0, 0x5024b4, 0x04, 0x01),
            (0xeae20, 0x502480, 0x5024b8, 0x04, 0x01),
        ]
        for variant, fields in enumerate(expected):
            out = fn(variant, 0x100 | fields[3], 0, 0x123456)
            assert (out.entry_address, out.flag_address, out.fallback_address,
                    out.flag_bit_mask, out.fallback_bit_mask, out.accepted,
                    out.returned_value, out.continuation_target) == (*fields, 1, 1, 0x123456)
            out = fn(variant, 0, fields[4], 0x123456)
            assert (out.accepted, out.returned_value) == (1, 1)
            out = fn(variant, 0, 0, 0x123456)
            assert (out.accepted, out.returned_value) == (0, 0)
        print("PASS: 0xeada0/0xeade0/0xeae20 runtime flag gates")


if __name__ == "__main__":
    main()
