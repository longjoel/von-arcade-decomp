#!/usr/bin/env python3
"""Validate the response-25 slot-20 continuation."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_87738_mode11_continuation.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "mode", "flag", "source_address", "source_value", "source_shifted",
        "mode_address", "flag_address", "shifted_address", "buffer_address",
        "helper_call", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "continuation.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_87738_mode11_continuation
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        result = Result()
        assert fn(0x89abcdef, ctypes.byref(result)) == 1
        assert result.mode == 11 and result.flag == 1
        assert result.source_address == 0x51c990 and result.source_value == 0x89abcdef
        assert result.source_shifted == 0x89abcd
        assert result.mode_address == 0x51c97c and result.flag_address == 0x51c9a0
        assert result.shifted_address == 0x51c994 and result.buffer_address == 0x503ad0
        assert result.helper_call == 0x8c970 and result.continuation_target == 0x878f8
    print("PASS: 0x87738 response-25 slot-20 continuation")


if __name__ == "__main__":
    main()
