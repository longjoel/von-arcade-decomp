#!/usr/bin/env python3
"""Validate the response-helper completion/retry gate at 0x8d090."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_8d090_completion_gate.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "status_word", "status_offset", "completion_address", "completion_value",
        "returned", "retry_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "gate.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8d090_completion_gate
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        for status, value, returned in ((0, 1, 1), (1, 0, 0), (0xffffffff, 0, 0)):
            result = Result()
            assert fn(status, ctypes.byref(result)) == 1
            assert (result.status_word, result.status_offset) == (status, 0x30)
            assert (result.completion_address, result.completion_value) == (0x51c9b4, value)
            assert result.returned == returned and result.retry_target == 0x8ccf0
    print("PASS: 0x8d090 response-helper completion gate")


if __name__ == "__main__":
    main()
