#!/usr/bin/env python3
"""Validate slot-12 ready/device branch ordering."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_1b5d8_device_gate.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "ready_address", "ready_value", "device_word_address", "device_word", "device_signed",
        "register_19_value", "expected_device_word", "device_low_halfword",
        "adjusted_status", "status_mask", "status_offset", "status_threshold",
        "branch", "return_target", "helper_call", "helper_continuation")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "gate.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_1b5d8_device_gate
        fn.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(0, 40, 9, ctypes.byref(result)) == 1
        assert result.branch == 1 and result.return_target == 0x1b95c

        result = Result()
        fn(1, 40, 9, ctypes.byref(result))
        assert result.expected_device_word == 40 and result.branch == 2
        assert result.helper_call == 0x43ee8 and result.helper_continuation == 0x423a8
        fn(1, 0x10028, 9, ctypes.byref(result))
        assert result.device_signed == 40 and result.branch == 2

        result = Result()
        fn(1, 0x1234, 9, ctypes.byref(result))
        assert result.adjusted_status == ((0x1234 + 0xffed) & 0xffff)
        assert result.branch == 1

        result = Result()
        fn(1, 0x13, 9, ctypes.byref(result))
        assert result.adjusted_status == ((0x13 + 0xffed) & 0xffff)
        assert result.branch == 2

    print("PASS: 0x1b5d8 slot-12 ready/device gate")


if __name__ == "__main__":
    main()
