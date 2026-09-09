#!/usr/bin/env python3
"""Validate the recovered slot-11 setup/arithmetic prefix."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_1afe0_prefix.c"


class Result(ctypes.Structure):
    _fields_ = [
        ("ready_address", ctypes.c_uint32), ("ready_value", ctypes.c_uint32),
        ("marker_address", ctypes.c_uint32), ("marker_value", ctypes.c_uint32),
        ("base_address", ctypes.c_uint32), ("base_value", ctypes.c_uint32),
        ("divisor_register", ctypes.c_uint32), ("divisor_value", ctypes.c_uint32),
        ("base_quotient", ctypes.c_uint32), ("base_remainder", ctypes.c_uint32),
        ("bucket_divisor", ctypes.c_uint32), ("bucket_quotient", ctypes.c_uint32),
        ("offset_value", ctypes.c_uint32), ("bucket_remainder", ctypes.c_uint32),
        ("scaled_remainder", ctypes.c_uint32), ("grid_index", ctypes.c_uint32),
        ("helper_call", ctypes.c_uint32), ("helper_argument", ctypes.c_uint32),
        ("timing_source_address", ctypes.c_uint32), ("timing_source_value", ctypes.c_uint32),
        ("row_address", ctypes.c_uint32), ("row_value", ctypes.c_uint32),
        ("timing_delta", ctypes.c_uint32), ("timing_table_address", ctypes.c_uint32),
        ("timing_table_index", ctypes.c_uint32), ("timing_table_write_address", ctypes.c_uint32),
        ("timing_table_write_value", ctypes.c_uint32), ("continuation_call", ctypes.c_uint32),
        ("continuation_target", ctypes.c_uint32), ("valid", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_1afe0_prefix
        fn.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(0, 0x1234, 9, 5, 0x1200, 3, 0, ctypes.byref(result)) == 1
        assert result.ready_address == 0x503a7c
        assert result.marker_address == 0x503a60 and result.marker_value == 0
        assert result.divisor_value == 40
        assert result.base_quotient == 0x1234 // 40
        assert result.base_remainder == 0x1234 % 40
        assert result.bucket_quotient == 0x1234 // 0xb40
        assert result.bucket_remainder == (5 + 31) % result.base_quotient
        assert result.grid_index == ((0x1234 % 40) * 99) // 40
        assert result.helper_call == 0x1e9e0 and result.helper_argument == result.grid_index
        assert result.timing_delta == 0x34
        assert result.timing_table_write_address == 0x503a30 + 3 * 4
        assert result.timing_table_write_value == 0x34
        assert result.continuation_call == 0xde630 and result.continuation_target == 0x1b054
        assert result.valid == 1

        result = Result()
        fn(0, 1213, 9, 29, 0, 3, 0, ctypes.byref(result))
        assert result.base_remainder == 13
        assert result.scaled_remainder == 13 * 99
        assert result.grid_index == (13 * 99) // 40

        result = Result()
        fn(1, 100, 9, 5, 90, 3, 7, ctypes.byref(result))
        assert result.marker_value == 7 and result.valid == 0
        assert result.helper_call == 0

    print("PASS: 0x1afe0 startup slot-11 setup prefix")


if __name__ == "__main__":
    main()
