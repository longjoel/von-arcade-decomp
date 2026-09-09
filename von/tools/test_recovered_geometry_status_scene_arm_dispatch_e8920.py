#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("input_mode", ctypes.c_uint32),
        ("accepted", ctypes.c_uint32),
        ("mode_address", ctypes.c_uint32),
        ("table_address", ctypes.c_uint32),
        ("target", ctypes.c_uint32),
        ("arm", ctypes.c_uint32 * 6),
        ("return_target", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-scene-arm-") as d:
        so = Path(d) / "scene-arm.so"
        subprocess.run([
            os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
            "-I", str(ROOT / "von/i960"), "-o", str(so),
            str(ROOT / "von/i960/recovered_geometry_status_scene_arm_dispatch_e8920.c")
        ], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_status_scene_arm_dispatch_e8920
        fn.argtypes = [ctypes.c_uint32]
        fn.restype = Result
        expected = [0xe8938, 0xe89d4, 0xe8ae0, 0xe8c5c, 0xe8e44, 0xe8fe4]
        for mode, target in enumerate(expected):
            out = fn(mode)
            assert out.accepted == 1
            assert out.target == target
        for mode in (6, 0xffffffff):
            out = fn(mode)
            assert out.accepted == 0
            assert out.target == 0xe9138
        out = fn(3)
        assert (out.mode_address, out.table_address,
                list(out.arm), out.return_target) == (
            0x5783c4, 0xe8920, expected, 0xe9138)
        print("PASS: 0xe8920 status-scene arm dispatch")


if __name__ == "__main__":
    main()
