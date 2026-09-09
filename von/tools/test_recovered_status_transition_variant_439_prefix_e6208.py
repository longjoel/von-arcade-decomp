#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("remainder", ctypes.c_uint32),
                ("route", ctypes.c_uint32),
                ("helper_target", ctypes.c_uint32),
                ("renderer_target", ctypes.c_uint32),
                ("record_base", ctypes.c_uint32),
                ("record_stride", ctypes.c_uint32),
                ("record_count", ctypes.c_uint32),
                ("first_text_column", ctypes.c_uint32),
                ("text_column_stride", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-variant-439-") as d:
        so = Path(d) / "status-variant-439.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_transition_variant_439_prefix_e6208.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_transition_variant_439_prefix_e6208
        fn.argtypes = [ctypes.c_uint32]
        fn.restype = Result

        fallthrough = fn(0x440)
        assert (fallthrough.route, fallthrough.continuation) == (0, 0xe6410)

        render = fn(0x439)
        assert (render.route, render.helper_target, render.renderer_target,
                render.record_base, render.record_stride, render.record_count,
                render.first_text_column, render.text_column_stride,
                render.continuation) == \
            (1, 0x1cac8, 0x1d880, 0x578460, 12, 5, 19, 3, 0xe6410)
        print("PASS: 0xe6208 state-1 remainder-0x439 renderer prefix")


if __name__ == "__main__":
    main()
