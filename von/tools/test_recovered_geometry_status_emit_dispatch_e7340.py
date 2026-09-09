#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("input_mode", ctypes.c_uint32),
                ("normalized_mode", ctypes.c_uint32),
                ("target", ctypes.c_uint32),
                ("mode_address", ctypes.c_uint32),
                ("variant_a", ctypes.c_uint32),
                ("variant_b", ctypes.c_uint32),
                ("variant_c", ctypes.c_uint32),
                ("variant_d", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-geometry-dispatch-") as d:
        so = Path(d) / "geometry-dispatch.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_status_emit_dispatch_e7340.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_status_emit_dispatch_e7340
        fn.argtypes = [ctypes.c_uint32]
        fn.restype = Result
        expected = {0: 0xe6d80, 1: 0xe6ef0, 2: 0xe7060, 3: 0xe71d0,
                    4: 0xe6d80, 0xffffffff: 0xe6d80}
        for mode, target in expected.items():
            out = fn(mode)
            assert out.target == target
            assert out.normalized_mode == (mode if mode <= 3 else 0)
        out = fn(2)
        assert (out.mode_address, out.variant_a, out.variant_b, out.variant_c,
                out.variant_d) == (0x5783dc, 0xe6d80, 0xe6ef0, 0xe7060, 0xe71d0)
        print("PASS: 0xe7340 geometry status emitter dispatch")


if __name__ == "__main__":
    main()
