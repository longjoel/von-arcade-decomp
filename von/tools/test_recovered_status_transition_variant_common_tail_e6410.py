#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("remainder", ctypes.c_uint32),
                ("route", ctypes.c_uint32),
                ("status_504d2c", ctypes.c_uint32),
                ("status_504d2e", ctypes.c_uint32),
                ("status_504d24", ctypes.c_uint32),
                ("status_504d26", ctypes.c_uint32),
                ("table_address", ctypes.c_uint32),
                ("table_halfword_count", ctypes.c_uint32),
                ("return_helper_target", ctypes.c_uint32),
                ("return_helper_remainder", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-variant-tail-") as d:
        so = Path(d) / "status-variant-tail.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_transition_variant_common_tail_e6410.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_transition_variant_common_tail_e6410
        fn.argtypes = [ctypes.c_uint32]
        fn.restype = Result
        table_value = lib.recovered_status_transition_variant_table_value_e6410
        table_value.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        table_value.restype = ctypes.c_uint32

        for remainder in (0x437, 0x479, 0x653, 0x695, 0xffffffff):
            out = fn(remainder)
            assert (out.route, out.table_address, out.table_halfword_count) == \
                (0, 0, 0)
            assert (out.return_helper_target, out.return_helper_remainder) == \
                (0x1c618, 0x86f)

        for remainder in (0x438, 0x478, 0x654, 0x694):
            out = fn(remainder)
            assert (out.route, out.status_504d2c, out.status_504d2e,
                    out.status_504d24, out.status_504d26, out.table_address,
                    out.table_halfword_count, out.return_helper_target,
                    out.return_helper_remainder, out.continuation) == \
                (1, 0x4000, 0, 0x8000, 0, 0x577bb0, 0x200, 0x1c618,
                 0x86f, 0xe64fc)

        assert table_value(0x438, 0x97) == 0
        assert table_value(0x438, 0x98) == 0x200
        assert table_value(0x438, 0x10f) == 0x200
        assert table_value(0x438, 0x110) == 0
        assert table_value(0x478, 0x98) == 0
        assert table_value(0x654, 0x98) == 0x200
        assert table_value(0x694, 0x10f) == 0
        assert table_value(0x695, 0x98) == 0
        print("PASS: 0xe6410 state-1 common transition tail")


if __name__ == "__main__":
    main()
