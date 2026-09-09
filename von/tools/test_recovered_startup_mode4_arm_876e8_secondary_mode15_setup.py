#!/usr/bin/env python3
"""Validate the secondary response-1 mode-15 setup."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_876e8_secondary_mode15_setup.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "mode", "flag", "source_address", "source_value", "mode_address",
        "flag_value", "buffer_address", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "setup.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_876e8_secondary_mode15_setup
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        result = Result()
        assert fn(0x89abcdef, ctypes.byref(result)) == 1
        assert result.mode == 15 and result.flag == 1
        assert result.source_address == 0x51c990 and result.source_value == 0x89abcdef
        assert result.mode_address == 0x51c97c and result.flag_value == 1
        assert result.buffer_address == 0x5040d0 and result.continuation_target == 0x87864
    print("PASS: 0x876e8 secondary response-1 setup")


if __name__ == "__main__":
    main()
