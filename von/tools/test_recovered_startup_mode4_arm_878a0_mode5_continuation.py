#!/usr/bin/env python3
"""Validate the secondary slot-20 mode-5 continuation."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_878a0_mode5_continuation.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "mode", "flag", "source_value", "source_shifted", "mode_address",
        "flag_address", "shifted_address", "buffer_address", "first_helper",
        "second_helper", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "continuation.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_878a0_mode5_continuation
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        result = Result()
        assert fn(0x12345678, ctypes.byref(result)) == 1
        assert result.mode == 5 and result.flag == 1
        assert result.source_shifted == 0x123456
        assert result.mode_address == 0x51c97c and result.flag_address == 0x51c9a0
        assert result.shifted_address == 0x51c994 and result.buffer_address == 0x5040d0
        assert result.first_helper == 0x888f0 and result.second_helper == 0x88af0
        assert result.continuation_target == 0x878f8
    print("PASS: 0x878a0 mode-5 slot-20 continuation")


if __name__ == "__main__":
    main()
