#!/usr/bin/env python3
"""Validate slot-20 response-0x25 wrapper arguments."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_8722c_response25.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "response_handler", "register_5_value", "source_address", "source_value",
        "register_4_value", "buffer_argument", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "response25.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8722c_response25
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(0x55, ctypes.byref(result)) == 1
        assert result.response_handler == 0x25 and result.register_5_value == 10
        assert result.source_address == 0x51c98c and result.source_value == 0x55
        assert result.register_4_value == 1 and result.buffer_argument == 0x5040d0
        assert result.continuation_target == 0x87738

    print("PASS: 0x8722c startup slot-20 response-25 wrapper")


if __name__ == "__main__":
    main()
