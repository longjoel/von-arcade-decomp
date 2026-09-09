#!/usr/bin/env python3
"""Validate slot-20 response-0x49 two-threshold wrapper."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_8729c_response49.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "response_handler", "real_input", "first_compare_low", "first_compare_high",
        "second_compare_low", "second_compare_high", "below_first_threshold",
        "below_second_threshold", "intermediate_path", "intermediate_register_5",
        "failure_target", "success_target", "intermediate_target", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "response49.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8729c_response49
        fn.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(1, 1, 1, ctypes.byref(result)) == 1
        assert result.continuation_target == 0x878e8

        result = Result()
        fn(2, 0, 1, ctypes.byref(result))
        assert result.intermediate_path == 1 and result.intermediate_register_5 == 6
        assert result.continuation_target == 0x87398

        result = Result()
        fn(3, 0, 0, ctypes.byref(result))
        assert result.intermediate_path == 0 and result.continuation_target == 0x87394
        assert result.first_compare_high == 0x40590000
        assert result.second_compare_high == 0x4072c000

    print("PASS: 0x8729c startup slot-20 response-49 wrapper")


if __name__ == "__main__":
    main()
