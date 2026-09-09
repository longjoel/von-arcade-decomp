#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("helper_target", ctypes.c_uint32),
                ("status_504d2c", ctypes.c_uint32),
                ("status_504d2e", ctypes.c_uint32),
                ("device_bit_address", ctypes.c_uint32),
                ("device_bit", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-special-") as d:
        so = Path(d) / "status-special.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_transition_gateway_special_438_e5dbc.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_transition_gateway_special_438_e5dbc
        fn.argtypes = [ctypes.POINTER(Result)]
        out = Result()
        fn(ctypes.byref(out))
        assert (out.helper_target, out.status_504d2c, out.status_504d2e,
                out.device_bit_address, out.device_bit, out.continuation) == \
            (0x1c618, 0xc000, 0x8000, 0x100a000, 9, 0xe60d0)
        print("PASS: 0xe5dbc exact-0x438 status arm")


if __name__ == "__main__":
    main()
