#!/usr/bin/env python3
"""Validate compact secondary slot-20 mode-entry stubs."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_secondary_mode_entries.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in ("mode", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "entries.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_secondary_mode_entry
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        for mode in (5, 11):
            result = Result()
            assert fn(mode, ctypes.byref(result)) == 1
            assert result.mode == mode and result.continuation_target == 0x87850
    print("PASS: secondary slot-20 mode-entry stubs")


if __name__ == "__main__":
    main()
