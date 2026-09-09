#!/usr/bin/env python3
"""Validate slot-20 response-0x1f comparison wrapper."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_87210_response1f.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "response_handler", "real_input", "real_compare_low", "real_compare_high",
        "real_less", "common_failure_target", "common_success_target",
        "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "response1f.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_87210_response1f
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(0x12345678, 1, ctypes.byref(result)) == 1
        assert result.response_handler == 0x1f
        assert result.real_compare_low == 0 and result.real_compare_high == 0x40590000
        assert result.continuation_target == 0x878e8

        result = Result()
        fn(0x87654321, 0, ctypes.byref(result))
        assert result.real_input == 0x87654321 and result.real_less == 0
        assert result.continuation_target == 0x87394

    print("PASS: 0x87210 startup slot-20 response-1f wrapper")


if __name__ == "__main__":
    main()
