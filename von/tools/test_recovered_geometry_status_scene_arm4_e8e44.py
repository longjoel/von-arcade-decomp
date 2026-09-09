#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("feature_flags", ctypes.c_uint32),
                ("object_tag", ctypes.c_uint32 * 3),
                ("admitted", ctypes.c_uint32),
                ("packet", ctypes.c_uint32 * 5),
                ("packet_count", ctypes.c_uint32),
                ("dispatch_target", ctypes.c_uint32),
                ("transform_0", ctypes.c_uint32),
                ("transform_1", ctypes.c_uint32 * 3),
                ("transform_2", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32),
                ("cleanup_target", ctypes.c_uint32),
                ("return_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-scene-arm4-") as d:
        so = Path(d) / "scene-arm4.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_status_scene_arm4_e8e44.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_status_scene_arm4_e8e44
        fn.argtypes = [ctypes.c_uint32] * 4
        fn.restype = Result
        for flags, admitted in ((0, 0), (8, 1), (0xffffffff, 1)):
            out = fn(flags, 0x1234, 0x5678, 0x9abc)
            assert out.admitted == admitted
            assert list(out.object_tag) == [0x34, 0x78, 0xbc]
        out = fn(8, 1, 2, 3)
        assert list(out.packet) == [5, 19, 0x41400000, 0x41400000, 0x3f800000]
        assert list(out.transform_1) == [0xc0c00000, 0, 0x40c00000]
        assert (out.packet_count, out.dispatch_target, out.transform_0,
                out.transform_2, out.completion_word, out.cleanup_target,
                out.return_target) == (
            5, 0xe7390, 0x49c980, 0xc0900000, 6, 0xe8fac, 0xe8fe0)
        print("PASS: 0xe8e44 status-scene arm 4")


if __name__ == "__main__":
    main()
