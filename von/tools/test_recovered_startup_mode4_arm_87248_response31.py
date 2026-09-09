#!/usr/bin/env python3
"""Validate slot-20 response-0x31 comparison wrapper."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_87248_response31.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "response_handler", "real_input", "real_compare_low", "real_compare_high",
        "real_less", "failure_target", "success_target", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "response31.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_87248_response31
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(0xabcdef01, 1, ctypes.byref(result)) == 1
        assert result.response_handler == 0x31
        assert result.real_compare_low == 0 and result.real_compare_high == 0x40590000
        assert result.continuation_target == 0x878e8

        result = Result()
        fn(0x10203040, 0, ctypes.byref(result))
        assert result.real_input == 0x10203040 and result.real_less == 0
        assert result.continuation_target == 0x87394

    print("PASS: 0x87248 startup slot-20 response-31 wrapper")


if __name__ == "__main__":
    main()
