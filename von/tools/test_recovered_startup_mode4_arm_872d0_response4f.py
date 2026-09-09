#!/usr/bin/env python3
"""Validate slot-20 response-0x4f wrapper stores."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_872d0_response4f.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "response_handler", "register_5_value", "source_address", "source_value",
        "register_4_value", "buffer_argument", "stored_mode_address", "stored_mode_value",
        "stored_flag_address", "stored_flag_value", "shifted_source_address",
        "shifted_source_value", "side_effect_call", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "response4f.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_872d0_response4f
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(0x12345678, ctypes.byref(result)) == 1
        assert result.response_handler == 0x4f and result.register_5_value == 4
        assert result.source_address == 0x51c98c and result.buffer_argument == 0x5040d0
        assert result.stored_mode_address == 0x51c97c and result.stored_mode_value == 4
        assert result.stored_flag_address == 0x51c9a0 and result.stored_flag_value == 1
        assert result.shifted_source_value == 0x00123456
        assert result.side_effect_call == 0x88a10 and result.continuation_target == 0x873cc

    print("PASS: 0x872d0 startup slot-20 response-4f wrapper")


if __name__ == "__main__":
    main()
