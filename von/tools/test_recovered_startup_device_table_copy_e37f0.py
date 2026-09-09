#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("first_source", ctypes.c_uint32),
                ("first_destination", ctypes.c_uint32),
                ("first_bytes", ctypes.c_uint32),
                ("second_source", ctypes.c_uint32),
                ("second_destination", ctypes.c_uint32),
                ("second_bytes", ctypes.c_uint32),
                ("copy_helper", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-device-copy-") as d:
        so = Path(d) / "device-copy.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_startup_device_table_copy_e37f0.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_startup_device_table_copy_e37f0
        fn.argtypes = [ctypes.POINTER(Result)]
        out = Result()
        fn(ctypes.byref(out))
        assert (out.first_source, out.first_destination, out.first_bytes,
                out.second_source, out.second_destination, out.second_bytes,
                out.copy_helper) == (0x1d00144, 0x578410, 0x50,
                                      0x1d00194, 0x578460, 0x78, 0xf5d40)
        print("PASS: 0xe37f0 startup/device table copy contract")


if __name__ == "__main__":
    main()
