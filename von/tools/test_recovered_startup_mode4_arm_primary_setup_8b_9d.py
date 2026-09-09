#!/usr/bin/env python3
"""Validate primary response-8b/9d setup wrappers."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_primary_setup_8b_9d.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("mode", "flag", "source_address", "source_value", "mode_address",
                 "flag_value", "buffer_address", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "setup.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_primary_setup_8b_9d
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        for mode in (10, 4):
            result = Result()
            assert fn(mode, 0x89abcdef, ctypes.byref(result)) == 1
            assert result.mode == mode and result.flag == 1
            assert result.source_address == 0x51c98c and result.source_value == 0x89abcdef
            assert result.mode_address == 0x51c97c and result.flag_value == 1
            assert result.buffer_address == 0x5040d0 and result.continuation_target == 0x87864
    print("PASS: primary response-8b/9d setup")


if __name__ == "__main__":
    main()
