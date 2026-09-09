#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("status_504d2c", ctypes.c_uint32),
                ("status_504d2e", ctypes.c_uint32),
                ("status_504d24", ctypes.c_uint32),
                ("device_bit_address", ctypes.c_uint32),
                ("device_bit", ctypes.c_uint32),
                ("renderer_arg0", ctypes.c_uint32),
                ("renderer_arg1", ctypes.c_uint32),
                ("helper_target", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-654-") as d:
        so = Path(d) / "status-654.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_transition_gateway_special_654_e5f48.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_transition_gateway_special_654_e5f48
        fn.argtypes = [ctypes.POINTER(Result)]
        out = Result()
        fn(ctypes.byref(out))
        assert (out.status_504d2c, out.status_504d2e, out.status_504d24,
                out.device_bit_address, out.device_bit) == (0xc000, 0x8000,
                0x200, 0x100a000, 9)
        assert (out.renderer_arg0, out.renderer_arg1, out.helper_target,
                out.continuation) == (13, 12, 0x1cac8, 0xe5f88)
        print("PASS: 0xe5f48 exact-0x654 status arm")


if __name__ == "__main__":
    main()
