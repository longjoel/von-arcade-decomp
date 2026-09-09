#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Input(ctypes.Structure):
    _fields_ = [("first_result_0", ctypes.c_uint32),
                ("first_result_1", ctypes.c_uint32),
                ("second_result_0", ctypes.c_uint32),
                ("second_result_1", ctypes.c_uint32),
                ("object_flag_1dd", ctypes.c_uint32),
                ("object_flag_1de", ctypes.c_uint32),
                ("object_flag_1df", ctypes.c_uint32)]


class Result(ctypes.Structure):
    _fields_ = [("first_pair", ctypes.c_uint32 * 2),
                ("second_pair", ctypes.c_uint32 * 2),
                ("control_504e30", ctypes.c_uint32),
                ("helper_target", ctypes.c_uint32),
                ("shared_output_offset", ctypes.c_uint32),
                ("shared_aux_offset", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-profile-publish-") as d:
        so = Path(d) / "profile-publish.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_profile_pair_publication_76934.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_profile_pair_publication_76934
        fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Result)]
        value = Input(1, 2, 3, 4, 1, 2, 2)
        out = Result()
        fn(ctypes.byref(value), ctypes.byref(out))
        assert list(out.first_pair) == [1, 2]
        assert list(out.second_pair) == [3, 4]
        assert out.control_504e30 == 0x2b
        assert (out.helper_target, out.shared_output_offset,
                out.shared_aux_offset) == (0x778b0, 0x40, 0x44)
        value.object_flag_1dd = 0
        value.object_flag_1de = 0
        value.object_flag_1df = 0
        fn(ctypes.byref(value), ctypes.byref(out))
        assert out.control_504e30 == 1
        print("PASS: 0x76934 paired publication and control-bit synthesis")


if __name__ == "__main__":
    main()
