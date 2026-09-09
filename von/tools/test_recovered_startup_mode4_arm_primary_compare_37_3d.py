#!/usr/bin/env python3
"""Validate primary response-37/3d compare wrappers."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_primary_compare_37_3d.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("real_value", "compare_pair_low", "compare_pair_high", "less_than",
                 "failure_target", "success_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "compare.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_primary_compare_37_3d
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        for predicate, expected in ((0, 0x87394), (1, 0x878e8), (0xffffffff, 0x878e8)):
            result = Result()
            assert fn(0xabcdef01, predicate, ctypes.byref(result)) == 1
            assert result.compare_pair_low == 0 and result.compare_pair_high == 0x40590000
            assert result.less_than == min(predicate, 1)
            target = result.failure_target if result.less_than else result.success_target
            assert target == expected
    print("PASS: primary response-37/3d compare")


if __name__ == "__main__":
    main()
