#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("object_tag", ctypes.c_uint32 * 3),
                ("packet", ctypes.c_uint32 * 5),
                ("packet_count", ctypes.c_uint32),
                ("dispatch_target", ctypes.c_uint32),
                ("transform_0", ctypes.c_uint32),
                ("transform_1", ctypes.c_uint32 * 3),
                ("transform_2", ctypes.c_uint32),
                ("completion_target", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32),
                ("return_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-scene-arm5-") as d:
        so = Path(d) / "scene-arm5.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_status_scene_arm5_e8fe4.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_status_scene_arm5_e8fe4
        fn.argtypes = [ctypes.c_uint32] * 3
        fn.restype = Result
        out = fn(0x1234, 0x5678, 0x9abc)
        assert list(out.object_tag) == [0x34, 0x78, 0xbc]
        assert list(out.packet) == [5, 19, 0x41400000, 0x41400000, 0x3f800000]
        assert list(out.transform_1) == [0xc0c00000, 0, 0x40c00000]
        assert (out.packet_count, out.dispatch_target, out.transform_0,
                out.transform_2, out.completion_target, out.completion_word,
                out.return_target) == (
            5, 0xe7390, 0x49c980, 0xc0900000, 0xe8e34, 6, 0xe9138)
        print("PASS: 0xe8fe4 status-scene arm 5")


if __name__ == "__main__":
    main()
