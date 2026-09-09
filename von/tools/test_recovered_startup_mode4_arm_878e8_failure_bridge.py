#!/usr/bin/env python3
"""Validate slot-20 failure-to-shared-tail bridge."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_878e8_failure_bridge.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "helper_call", "helper_result", "mask", "stored_address", "stored_value",
        "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "bridge.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_878e8_failure_bridge
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        for helper_result, expected in ((0, 0), (1, 1), (0x12345678, 0), (0xffffffff, 1)):
            result = Result()
            assert fn(helper_result, ctypes.byref(result)) == 1
            assert result.helper_call == 0xf5058 and result.helper_result == helper_result
            assert result.mask == 1 and result.stored_address == 0x51c97c
            assert result.stored_value == expected and result.continuation_target == 0x878f8

    print("PASS: 0x878e8 startup slot-20 failure bridge")


if __name__ == "__main__":
    main()
