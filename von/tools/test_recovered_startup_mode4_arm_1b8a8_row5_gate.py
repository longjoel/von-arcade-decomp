#!/usr/bin/env python3
"""Validate slot-12 row-5 quotient phase routing."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_1b8a8_row5_gate.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "row_value", "row_gate", "base_address", "base_value", "divisor_address",
        "divisor_value", "quotient", "quotient_threshold", "quotient_high",
        "register_19_value", "command_address", "command_value", "state_address",
        "state_value", "row_address", "row_publication", "progress_address",
        "progress_value", "progress_written", "mmio_address", "mmio_before",
        "mmio_after", "mmio_bit_set", "branch", "continuation_target", "valid")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "row5.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_1b8a8_row5_gate
        fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(5, 0x690 * 2, 2, 9, 0x33, 0x20, ctypes.byref(result)) == 1
        assert result.quotient == 0x690 and result.quotient_high == 0
        assert result.state_value == 6 and result.row_publication == 6
        assert result.mmio_after == 0x20 and result.mmio_bit_set == 0
        assert result.command_value == 40 and result.continuation_target == 0x1b924

        result = Result()
        fn(5, 0x691 * 2, 2, 9, 0x33, 0x20, ctypes.byref(result))
        assert result.quotient_high == 1 and result.state_value == 27
        assert result.progress_value == 0x33 and result.progress_written == 1
        assert result.mmio_after == 0x21 and result.continuation_target == 0x1b940
        assert result.valid == 1

        result = Result()
        fn(5, ctypes.c_uint32(-0x690 * 2).value, 2, 9, 0x33, 0x20,
           ctypes.byref(result))
        assert result.quotient == ctypes.c_uint32(-0x690).value
        assert result.quotient_high == 0 and result.state_value == 6
        assert result.continuation_target == 0x1b924

        result = Result()
        fn(5, 0x691 * 2, 2, 0xffff, 0x33, 0x10020, ctypes.byref(result))
        assert result.command_value == 0x1e
        fn(5, 0x691 * 2, 2, 9, 0x33, 0x8000, ctypes.byref(result))
        assert result.mmio_before == 0xffff8000 and result.mmio_after == 0x8001

        result = Result()
        fn(4, 100, 2, 9, 0x33, 0, ctypes.byref(result))
        assert result.branch == 1 and result.continuation_target == 0x1b914

    print("PASS: 0x1b8a8 slot-12 row-5 gate")


if __name__ == "__main__":
    main()
