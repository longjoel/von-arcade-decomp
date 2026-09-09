#!/usr/bin/env python3
"""Validate slot-12 progress setup/countdown routing."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_1b598_progress_gate.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "progress_address", "progress_before", "progress_after", "setup_argument",
        "setup_call", "setup_requested", "high_progress_threshold", "high_progress_path",
        "control_address", "control_value", "control_bit4", "countdown_performed",
        "progress_write_address", "progress_write_value", "countdown_zero",
        "device_gate_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "gate.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_1b598_progress_gate
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(1, 0, ctypes.byref(result)) == 1
        assert result.setup_requested == 1 and result.setup_argument == 3
        assert result.countdown_zero == 1 and result.progress_after == 0

        result = Result()
        fn(0xb0, 0x10, ctypes.byref(result))
        assert result.high_progress_path == 1 and result.control_bit4 == 1
        assert result.setup_requested == 0 and result.countdown_performed == 0
        assert result.progress_after == 0xb0 and result.progress_write_address == 0
        assert result.device_gate_target == 0x1b614

        result = Result()
        fn(7, 0, ctypes.byref(result))
        assert result.progress_after == 6 and result.high_progress_path == 0
        assert result.countdown_performed == 1 and result.progress_write_value == 6
        assert result.countdown_zero == 0 and result.device_gate_target == 0x1b5d8

        result = Result()
        fn(0x800000b0, 0x10, ctypes.byref(result))
        assert result.high_progress_path == 0 and result.countdown_performed == 1
        assert result.progress_after == 0x800000af
        assert result.device_gate_target == 0x1b5d8

    print("PASS: 0x1b598 slot-12 progress gate")


if __name__ == "__main__":
    main()
