#!/usr/bin/env python3
"""Validate the slot-20 secondary setup wrapper."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_87850_shared_setup.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("mode", "source_address", "source_value", "flag", "buffer_address", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "setup.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_87850_shared_setup
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        for mode in (5, 11):
            result = Result()
            assert fn(mode, 0xdeadbeef, ctypes.byref(result)) == 1
            assert result.mode == mode and result.source_address == 0x51c990
            assert result.source_value == 0xdeadbeef and result.flag == 1
            assert result.buffer_address == 0x503ad0 and result.continuation_target == 0x87864
    print("PASS: 0x87850 secondary slot-20 setup")


if __name__ == "__main__":
    main()
