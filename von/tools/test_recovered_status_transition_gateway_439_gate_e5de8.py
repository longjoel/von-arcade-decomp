#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("remainder", ctypes.c_int32),
                ("route", ctypes.c_uint32),
                ("target", ctypes.c_uint32),
                ("tested_value", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-439-") as d:
        so = Path(d) / "status-439.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_transition_gateway_439_gate_e5de8.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_transition_gateway_439_gate_e5de8
        fn.argtypes = [ctypes.c_int32]
        fn.restype = Result
        assert (fn(0x439).route, fn(0x439).target, fn(0x439).tested_value) == (0, 0xe5df0, 0x439)
        assert (fn(0x43a).route, fn(0x43a).target) == (1, 0xe5f48)
        assert (fn(-1).route, fn(-1).target) == (1, 0xe5f48)
        print("PASS: 0xe5de8 exact-0x439 gateway gate")


if __name__ == "__main__":
    main()
