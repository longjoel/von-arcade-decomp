#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("feature_flags", ctypes.c_uint32),
                ("scene_count", ctypes.c_uint32),
                ("object_tag", ctypes.c_uint32),
                ("admitted", ctypes.c_uint32),
                ("fifo_word", ctypes.c_uint32 * 5),
                ("fifo_count", ctypes.c_uint32),
                ("object_dispatch_target", ctypes.c_uint32),
                ("transform_0", ctypes.c_uint32),
                ("transform_1", ctypes.c_uint32),
                ("transform_2", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32),
                ("return_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-scene-arm0-") as d:
        so = Path(d) / "scene-arm0.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_status_scene_arm0_e8938.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_status_scene_arm0_e8938
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        fn.restype = Result
        for flags, admitted in ((0, 0), (1 << 3, 1), (0xffffffff, 1)):
            out = fn(flags, 7, 0x1234)
            assert out.admitted == admitted
            assert out.object_tag == 0x34
        out = fn(1 << 3, 7, 0x12)
        assert list(out.fifo_word) == [5, 19, 0x41400000, 0x41400000, 0x3f800000]
        assert (out.fifo_count, out.object_dispatch_target,
                out.transform_0, out.transform_1, out.transform_2,
                out.completion_word, out.return_target) == (
            5, 0xe7390, 0x49c980, 0xc0c00000, 0xc0900000, 6, 0xe89d0)
        print("PASS: 0xe8938 status-scene arm 0")


if __name__ == "__main__":
    main()
