#!/usr/bin/env python3
"""Validate slot-12 counter comparison and branch ordering."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_1b61c_counter_dispatch.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "progress_address", "progress_value", "limit_address", "limit_value",
        "secondary_counter_address", "secondary_counter_value", "progress_exceeded",
        "secondary_within_limit", "selected_state", "branch", "helper_call",
        "helper_target", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "dispatch.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_1b61c_counter_dispatch
        fn.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(4, 4, 4, ctypes.byref(result)) == 1
        assert result.selected_state == 8 and result.branch == 1
        assert result.continuation_target == 0x1b800

        result = Result()
        fn(5, 4, 4, ctypes.byref(result))
        assert result.progress_exceeded == 1 and result.secondary_within_limit == 1
        assert result.branch == 2 and result.continuation_target == 0x1b780

        result = Result()
        fn(5, 4, 5, ctypes.byref(result))
        assert result.branch == 3 and result.helper_call == 0x31c0
        assert result.helper_target == result.continuation_target == 0x1b650

        result = Result()
        fn(4, 4, 5, ctypes.byref(result))
        assert result.progress_exceeded == 0 and result.secondary_within_limit == 0
        assert result.branch == 3 and result.helper_call == 0x31c0

        result = Result()
        fn(ctypes.c_uint32(-1).value, 0, 0, ctypes.byref(result))
        assert result.progress_exceeded == 0 and result.branch == 1

    print("PASS: 0x1b61c slot-12 counter dispatcher")


if __name__ == "__main__":
    main()
