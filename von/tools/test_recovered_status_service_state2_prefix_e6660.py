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
                ("helper_target", ctypes.c_uint32),
                ("status_504d2c", ctypes.c_uint32),
                ("status_504d24", ctypes.c_uint32),
                ("status_504d2e", ctypes.c_uint32),
                ("device_bit_address", ctypes.c_uint32),
                ("device_bit", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32),
                ("modulus", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-state2-") as d:
        so = Path(d) / "status-state2.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_service_state2_prefix_e6660.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_service_state2_prefix_e6660
        fn.argtypes = [ctypes.c_int32]
        fn.restype = Result

        early = fn(0x437)
        assert (early.remainder, early.route, early.target) == (0x437, 0, 0xe6678)
        special = fn(0x438)
        assert (special.route, special.target, special.helper_target,
                special.status_504d2c, special.status_504d24, special.status_504d2e,
                special.device_bit_address, special.device_bit,
                special.continuation) == \
            (1, 0xe6680, 0x1c618, 0xc000, 0x200, 0x8000, 0x100a000, 9,
             0xe6c50)
        general = fn(0x439)
        assert (general.route, general.target) == (2, 0xe66b4)
        negative = fn(-1)
        assert negative.route == 0
        print("PASS: 0xe6660 state-2 status prefix")


if __name__ == "__main__":
    main()
