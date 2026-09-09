#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("input_selector", ctypes.c_uint32),
                ("bounded_selector", ctypes.c_uint32),
                ("selected_profile", ctypes.c_uint32),
                ("dispatch_table", ctypes.c_uint32),
                ("loop_target", ctypes.c_uint32),
                ("return_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-profile-dispatch-") as d:
        so = Path(d) / "status-profile-dispatch.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_profile_selector_dispatch_e6500.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_profile_selector_dispatch_e6500
        fn.argtypes = [ctypes.c_uint32]
        fn.restype = Result

        expected = (0, 4, 3, 7, 1, 2, 6, 5)
        for selector, profile in enumerate(expected):
            out = fn(selector)
            assert (out.bounded_selector, out.selected_profile) == (selector, profile)
        for selector in (8, 0xffffffff):
            out = fn(selector)
            assert (out.bounded_selector, out.selected_profile) == (0, 0)
        assert (out.dispatch_table, out.loop_target, out.return_target) == \
            (0xe651c, 0xe6578, 0xe6640)
        print("PASS: 0xe6500 status profile selector dispatch")


if __name__ == "__main__":
    main()
