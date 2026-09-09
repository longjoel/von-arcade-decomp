#!/usr/bin/env python3
"""Validate the secondary response-1f compare wrapper."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_87704_secondary_compare_1f.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "real_value", "compare_low", "compare_high", "low_pair_word", "high_pair_word",
        "less_than", "failure_target", "success_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "compare.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_87704_secondary_compare_1f
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        for predicate, target in ((0, 0x878a0), (1, 0x878e8), (2, 0x878e8)):
            result = Result()
            assert fn(0x12345678, predicate, ctypes.byref(result)) == 1
            assert result.compare_low == 0x40590000 and result.high_pair_word == 0x40590000
            assert result.low_pair_word == 0 and result.less_than == min(predicate, 1)
            assert (result.failure_target if result.less_than else result.success_target) == (0x878e8 if predicate else target)
    print("PASS: 0x87704 secondary response-1f compare")


if __name__ == "__main__":
    main()
