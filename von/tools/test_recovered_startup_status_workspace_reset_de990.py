#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Input(ctypes.Structure):
    _fields_ = [("stage_503b00", ctypes.c_int32),
                ("state_504100", ctypes.c_int32),
                ("mode_504134", ctypes.c_int32)]


class Result(ctypes.Structure):
    _fields_ = [("cleared_503c9c", ctypes.c_uint32),
                ("cleared_503c98", ctypes.c_uint32),
                ("cleared_50429c", ctypes.c_uint32),
                ("cleared_504298", ctypes.c_uint32),
                ("mode_is_9", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-startup-reset-") as d:
        so = Path(d) / "startup-reset.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_startup_status_workspace_reset_de990.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_startup_status_workspace_reset_de990
        fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Result)]
        out = Result()
        value = Input(4, 1, 9)
        fn(ctypes.byref(value), ctypes.byref(out))
        assert (out.cleared_503c9c, out.cleared_503c98,
                out.cleared_50429c, out.cleared_504298,
                out.mode_is_9, out.continuation) == (1, 1, 1, 1, 1, 0xde9ec)
        value = Input(4, 0, 8)
        fn(ctypes.byref(value), ctypes.byref(out))
        assert (out.cleared_50429c, out.cleared_504298,
                out.mode_is_9, out.continuation) == (0, 0, 0, 0xdead4)
        print("PASS: 0xde990 startup workspace reset and mode split")


if __name__ == "__main__":
    main()
