#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("timer_value", ctypes.c_int32),
                ("remainder", ctypes.c_int32),
                ("route", ctypes.c_uint32),
                ("target", ctypes.c_uint32),
                ("modulus", ctypes.c_uint32),
                ("special_remainder", ctypes.c_uint32),
                ("lower_bound", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-gateway-") as d:
        so = Path(d) / "status-gateway.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_transition_gateway_prefix_e5da0.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_transition_gateway_prefix_e5da0
        fn.argtypes = [ctypes.c_int32]
        fn.restype = Result
        assert (fn(0).remainder, fn(0).route, fn(0).target) == (0, 0, 0xe5db0)
        assert (fn(0x437).remainder, fn(0x437).route) == (0x437, 0)
        assert (fn(0x438).route, fn(0x438).target) == (1, 0xe5dbc)
        assert (fn(0x439).route, fn(0x439).target) == (2, 0xe5de8)
        assert fn(-1).remainder == -1 and fn(-1).route == 0
        print("PASS: 0xe5da0 signed modulo and early-window routing")


if __name__ == "__main__":
    main()
