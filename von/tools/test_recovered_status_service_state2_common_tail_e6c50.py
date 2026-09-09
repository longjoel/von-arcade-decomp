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
    with tempfile.TemporaryDirectory(prefix="von-status-state2-tail-") as d:
        so = Path(d) / "status-state2-tail.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_service_state2_common_tail_e6c50.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_service_state2_common_tail_e6c50
        fn.argtypes = [ctypes.c_uint32]
        fn.restype = Result
        table_value = lib.recovered_status_service_state2_table_value_e6c50
        table_value.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        table_value.restype = ctypes.c_uint32

        for remainder in (0x437, 0x479, 0x653, 0x695, 0xffffffff):
            out = fn(remainder)
            assert (out.route, out.table_address, out.table_halfword_count,
                    out.continuation) == (0, 0, 0, 0xe6d3c)
        for remainder in (0x438, 0x478, 0x654, 0x694):
            out = fn(remainder)
            assert (out.route, out.status_504d2c, out.status_504d2e,
                    out.status_504d24, out.status_504d26, out.table_address,
                    out.table_halfword_count, out.continuation) == \
                (1, 0x4000, 0, 0x8000, 0, 0x577fb0, 0x200, 0xe6d3c)

        assert table_value(0x438, 0x62) == 0
        assert table_value(0x438, 0x63) == 0x200
        assert table_value(0x438, 0x123) == 0x200
        assert table_value(0x438, 0x124) == 0
        assert table_value(0x478, 0x63) == 0
        assert table_value(0x654, 0x63) == 0x200
        assert table_value(0x694, 0x123) == 0
        print("PASS: 0xe6c50 state-2 common status tail")


if __name__ == "__main__":
    main()
