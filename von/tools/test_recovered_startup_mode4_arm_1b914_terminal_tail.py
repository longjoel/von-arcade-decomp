#!/usr/bin/env python3
"""Validate slot-12 terminal command/row publication."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_1b914_terminal_tail.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "row_address", "row_value", "row_gate", "row_match", "register_19_value",
        "command_address", "command_value", "state_address", "state_value", "state_published",
        "row_publication_address", "row_publication_value", "record_helper_call",
        "setup_argument", "setup_call", "return_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_1b914_terminal_tail
        fn.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(6, 9, 7, ctypes.byref(result)) == 1
        assert result.row_match == 1 and result.state_value == 28
        assert result.command_value == 40 and result.row_publication_value == 6
        assert result.record_helper_call == 0x1fe90 and result.setup_call == 0x2a4e0
        assert result.return_target == 0x1b95c

        result = Result()
        fn(4, 9, 7, ctypes.byref(result))
        assert result.row_match == 0 and result.state_value == 7
        assert result.command_value == 40 and result.row_publication_value == 4

        result = Result()
        fn(4, 0xffff, 7, ctypes.byref(result))
        assert result.command_value == 0x1e

    print("PASS: 0x1b914 slot-12 terminal tail")


if __name__ == "__main__":
    main()
