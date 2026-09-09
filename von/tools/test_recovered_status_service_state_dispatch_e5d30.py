#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("target", ctypes.c_uint32),
                ("board_byte_admitted", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-dispatch-") as d:
        so = Path(d) / "status-dispatch.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_service_state_dispatch_e5d30.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_service_state_dispatch_e5d30
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        fn.restype = Result
        assert (fn(0, 1).route, fn(0, 1).target, fn(0, 1).board_byte_admitted) == (0, 0, 0)
        assert (fn(1, 0).route, fn(1, 0).target) == (1, 0xe5da0)
        assert (fn(1, 1).route, fn(1, 1).target) == (2, 0xe61c0)
        assert (fn(1, 2).route, fn(1, 2).target) == (3, 0xe6660)
        assert (fn(1, 7).route, fn(1, 7).target) == (1, 0xe5da0)
        print("PASS: 0xe5d30 board gate and state dispatch")


if __name__ == "__main__":
    main()
