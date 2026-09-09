#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Input(ctypes.Structure):
    _fields_ = [("global_504d94", ctypes.c_uint32),
                ("global_504db4", ctypes.c_uint32),
                ("normalized_geometry_bits", ctypes.c_uint32)]


class Result(ctypes.Structure):
    _fields_ = [("profile_index", ctypes.c_uint32),
                ("valid_profile_index", ctypes.c_uint32),
                ("dispatch_target", ctypes.c_uint32),
                ("special_geometry_override", ctypes.c_uint32),
                ("geometry_bits", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-profile-dispatch-") as d:
        so = Path(d) / "profile-dispatch.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_match_geometry_profile_dispatch_77470.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_match_geometry_profile_dispatch_77470
        fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Result)]
        result = Result()
        value = Input(1, 0, 0x12345678)
        fn(ctypes.byref(value), ctypes.byref(result))
        assert (result.profile_index, result.dispatch_target,
                result.special_geometry_override, result.geometry_bits) == (0, 0x775e0, 1, 0x42c80000)
        value.global_504d94 = 7
        value.global_504db4 = 1
        fn(ctypes.byref(value), ctypes.byref(result))
        assert (result.profile_index, result.dispatch_target,
                result.special_geometry_override, result.geometry_bits) == (6, 0x77834, 0, 0x12345678)
        value.global_504d94 = 21
        fn(ctypes.byref(value), ctypes.byref(result))
        assert result.valid_profile_index and result.dispatch_target == 0x777b0
        value.global_504d94 = 22
        fn(ctypes.byref(value), ctypes.byref(result))
        assert not result.valid_profile_index and result.dispatch_target == 0x77834
        print("PASS: 0x77470 profile index, override, and dispatch table")


if __name__ == "__main__":
    main()
