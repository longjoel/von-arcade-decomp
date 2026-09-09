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
                ("object_tag", ctypes.c_uint32 * 4),
                ("fourth_call_admitted", ctypes.c_uint32),
                ("packet", ctypes.c_uint32 * 5),
                ("packet_count", ctypes.c_uint32),
                ("dispatch_target", ctypes.c_uint32),
                ("transform_0", ctypes.c_uint32),
                ("transform_1", ctypes.c_uint32 * 4),
                ("transform_2", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32),
                ("cleanup_counter_before", ctypes.c_uint32),
                ("cleanup_counter_after", ctypes.c_uint32),
                ("cleanup_triggered", ctypes.c_uint32),
                ("cleanup_count_address", ctypes.c_uint32),
                ("frame_count_address", ctypes.c_uint32),
                ("cleanup_helper_a", ctypes.c_uint32),
                ("cleanup_helper_b", ctypes.c_uint32),
                ("return_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-scene-arm3-") as d:
        so = Path(d) / "scene-arm3.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_status_scene_arm3_e8c5c.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_status_scene_arm3_e8c5c
        fn.argtypes = [ctypes.c_uint32] * 7
        fn.restype = Result
        for flags, admitted in ((0, 0), (8, 1)):
            out = fn(flags, 4, 0x1234, 0x5678, 0x9abc, 0xdef0, 3)
            assert out.fourth_call_admitted == admitted
            assert list(out.object_tag) == [0x34, 0x78, 0xbc, 0xf0]
        out = fn(8, 4, 1, 2, 3, 4, 1)
        assert list(out.packet) == [5, 19, 0x41400000, 0x41400000, 0x3f800000]
        assert list(out.transform_1) == [0xc0c00000, 0, 0x40c00000, 0x41400000]
        assert (out.packet_count, out.dispatch_target, out.transform_0,
                out.transform_2, out.completion_word,
                out.cleanup_counter_after, out.cleanup_triggered,
                out.cleanup_count_address, out.frame_count_address,
                out.cleanup_helper_a, out.cleanup_helper_b,
                out.return_target) == (
            5, 0xe7390, 0x49c980, 0xc0900000, 6, 0, 1,
            0x503a04, 0x503a00, 0xe54a0, 0xe37b0, 0xe8e40)
        print("PASS: 0xe8c5c status-scene arm 3")


if __name__ == "__main__":
    main()
