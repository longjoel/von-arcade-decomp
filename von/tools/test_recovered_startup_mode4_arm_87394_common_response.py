#!/usr/bin/env python3
"""Validate slot-20 shared response continuation."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_87394_common_response.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "register_5_value", "source_address", "source_value", "register_4_value",
        "mode_address", "mode_value", "flag_address", "flag_value",
        "shifted_source_address", "shifted_source_value", "first_helper_call",
        "buffer_address", "second_helper_call", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "common.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_87394_common_response
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(0x12345678, ctypes.byref(result)) == 1
        assert result.register_5_value == 4 and result.register_4_value == 1
        assert result.source_address == 0x51c98c and result.source_value == 0x12345678
        assert result.mode_address == 0x51c97c and result.mode_value == 4
        assert result.flag_address == 0x51c9a0 and result.flag_value == 1
        assert result.shifted_source_value == 0x00123456
        assert result.first_helper_call == 0x888f0
        assert result.buffer_address == 0x503ad0 and result.second_helper_call == 0x88af0
        assert result.continuation_target == 0x878f8

    print("PASS: 0x87394 shared slot-20 response continuation")


if __name__ == "__main__":
    main()
