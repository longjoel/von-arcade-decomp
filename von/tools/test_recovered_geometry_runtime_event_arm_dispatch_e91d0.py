#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("input_counter", ctypes.c_uint32),
                ("remainder", ctypes.c_uint32),
                ("accepted", ctypes.c_uint32),
                ("counter_address", ctypes.c_uint32),
                ("table_address", ctypes.c_uint32),
                ("target", ctypes.c_uint32),
                ("fallback_target", ctypes.c_uint32),
                ("arm", ctypes.c_uint32 * 12)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-event-arm-") as d:
        so = Path(d) / "event-arm.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_runtime_event_arm_dispatch_e91d0.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_runtime_event_arm_dispatch_e91d0
        fn.argtypes = [ctypes.c_uint32]
        fn.restype = Result
        expected = [0xe9470, 0xe95a4, 0xe9da8, 0xea1a0,
                    0xe9da8, 0xea1a0, 0xea598, 0xea610,
                    0xe96b8, 0xe99fc, 0xe9bcc, 0xe9220]
        for counter in range(24):
            out = fn(counter)
            assert out.accepted == 1
            assert out.remainder == counter % 12
            assert out.target == expected[counter % 12]
        out = fn(0xffffffff)
        assert out.remainder == 3
        assert out.target == 0xea1a0
        assert (out.counter_address, out.table_address,
                out.fallback_target, list(out.arm)) == (
            0x5783fc, 0xe91f0, 0xea744, expected)
        print("PASS: 0xe91d0 runtime event arm dispatch")


if __name__ == "__main__":
    main()
