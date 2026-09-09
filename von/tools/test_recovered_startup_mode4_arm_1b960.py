#!/usr/bin/env python3
"""Validate compact slot-15 state publication."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_1b960.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "setup_call", "incoming_value", "value_address", "value", "state_address",
        "state", "return_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "slot13.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_1b960
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(0x12345678, ctypes.byref(result)) == 1
        assert result.setup_call == 0x29c08
        assert result.value_address == 0x5024c6 and result.value == 0x78
        assert result.state_address == 0x503a00 and result.state == 25
        assert result.return_target == 0x1b97c

        result = Result()
        assert fn(0x12345678, ctypes.byref(result)) == 1
        assert result.value == 0x78

    print("PASS: 0x1b960 startup slot 15")


if __name__ == "__main__":
    main()
