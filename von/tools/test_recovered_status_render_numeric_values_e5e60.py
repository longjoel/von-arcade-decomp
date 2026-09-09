#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("record_value", ctypes.c_int32),
                ("first_value", ctypes.c_int32),
                ("second_remainder", ctypes.c_int32),
                ("third_value", ctypes.c_int32),
                ("first_divisor", ctypes.c_uint32),
                ("second_divisor", ctypes.c_uint32),
                ("third_scale", ctypes.c_uint32),
                ("first_formatter", ctypes.c_uint32),
                ("second_formatter", ctypes.c_uint32),
                ("third_formatter", ctypes.c_uint32),
                ("separator_asset", ctypes.c_uint32),
                ("suffix_asset", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-numeric-") as d:
        so = Path(d) / "status-numeric.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_render_numeric_values_e5e60.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_render_numeric_values_e5e60
        fn.argtypes = [ctypes.c_int32]
        fn.restype = Result
        out = fn(5760 + 47)
        assert (out.first_value, out.second_remainder, out.third_value) == (2, 0, 32)
        assert (out.first_divisor, out.second_divisor, out.third_scale) == (0xb40, 48, 33)
        assert (out.first_formatter, out.second_formatter, out.third_formatter,
                out.separator_asset, out.suffix_asset) == (0xe3a10, 0xe3a10,
                0xe3a10, 0xe3b5a, 0xe3b5c)
        negative = fn(-1)
        assert (negative.first_value, negative.second_remainder,
                negative.third_value) == (0, 0, 0)
        print("PASS: 0xe5e60 numeric status-render values")


if __name__ == "__main__":
    main()
