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
                ("fixed_object_tag_0", ctypes.c_uint32),
                ("fixed_object_tag_1", ctypes.c_uint32),
                ("indexed_object_tag", ctypes.c_uint32),
                ("third_call_admitted", ctypes.c_uint32),
                ("packet", ctypes.c_uint32 * 5),
                ("packet_count", ctypes.c_uint32),
                ("dispatch_target", ctypes.c_uint32),
                ("common_transform_0", ctypes.c_uint32),
                ("first_transform_1", ctypes.c_uint32),
                ("common_transform_2", ctypes.c_uint32),
                ("third_transform_1", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32),
                ("return_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-scene-arm2-") as d:
        so = Path(d) / "scene-arm2.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_status_scene_arm2_e8ae0.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_status_scene_arm2_e8ae0
        fn.argtypes = [ctypes.c_uint32] * 5
        fn.restype = Result
        for flags, admitted in ((0, 0), (8, 1), (0xffffffff, 1)):
            out = fn(flags, 4, 0x1234, 0x5678, 0x9abc)
            assert out.third_call_admitted == admitted
            assert (out.fixed_object_tag_0, out.fixed_object_tag_1,
                    out.indexed_object_tag) == (0x34, 0x78, 0xbc)
        out = fn(8, 4, 0x12, 0x34, 0x56)
        assert list(out.packet) == [5, 19, 0x41400000, 0x41400000, 0x3f800000]
        assert (out.packet_count, out.dispatch_target, out.common_transform_0,
                out.first_transform_1, out.common_transform_2,
                out.third_transform_1, out.completion_word,
                out.return_target) == (
            5, 0xe7390, 0x49c980, 0xc0c00000, 0xc0900000,
            0x40c00000, 6, 0xe8c58)
        print("PASS: 0xe8ae0 status-scene arm 2")


if __name__ == "__main__":
    main()
