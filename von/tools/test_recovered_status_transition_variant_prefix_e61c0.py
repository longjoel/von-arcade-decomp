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
                ("continuation", ctypes.c_uint32),
                ("modulus", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-variant-") as d:
        so = Path(d) / "status-variant.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_transition_variant_prefix_e61c0.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_transition_variant_prefix_e61c0
        fn.argtypes = [ctypes.c_int32]
        fn.restype = Result
        assert (fn(0x437).route, fn(0x437).target) == (0, 0xe61d0)
        special = fn(0x438)
        assert (special.route, special.target, special.continuation) == (1, 0xe61dc, 0xe6410)
        assert (fn(0x439).route, fn(0x439).target) == (2, 0xe6208)
        assert fn(-1).remainder == -1 and fn(-1).target == 0xe61d0
        print("PASS: 0xe61c0 state-1 gateway remainder variant")


if __name__ == "__main__":
    main()
