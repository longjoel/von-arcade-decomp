#!/usr/bin/env python3
"""Validate the slot-20 buffer continuation."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_878d8_buffer_continuation.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("buffer_address", "helper_call", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "continuation.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_878d8_buffer_continuation
        fn.argtypes = [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        result = Result()
        assert fn(ctypes.byref(result)) == 1
        assert result.buffer_address == 0x5040d0
        assert result.helper_call == 0x88af0
        assert result.continuation_target == 0x878f8
    print("PASS: 0x878d8 slot-20 buffer continuation")


if __name__ == "__main__":
    main()
