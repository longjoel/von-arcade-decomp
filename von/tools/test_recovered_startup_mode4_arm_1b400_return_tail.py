#!/usr/bin/env python3
"""Validate slot-11 terminal state and command publication."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_1b400_return_tail.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "status_address", "status_value", "state_input", "state_publication_address",
        "state_publication", "progress_address", "progress_value", "counter_address",
        "counter_value", "limit_value", "ready_address", "ready_value", "command_address",
        "command_value", "command_published", "return_address")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_1b400_return_tail
        fn.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(0, 7, 4, 4, 0, ctypes.byref(result)) == 1
        assert result.state_publication == 31
        assert result.command_published == 1 and result.command_value == 20
        assert result.progress_value == 90 and result.return_address == 0x1b460

        result = Result()
        fn(1, 7, 5, 4, 0, ctypes.byref(result))
        assert result.state_publication == 38 and result.command_published == 0

        result = Result()
        fn(1, 7, 0x80000000, 0, 0, ctypes.byref(result))
        assert result.command_published == 1

    print("PASS: 0x1b400 slot-11 return/publication tail")


if __name__ == "__main__":
    main()
