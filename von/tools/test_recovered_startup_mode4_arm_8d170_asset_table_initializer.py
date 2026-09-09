#!/usr/bin/env python3
"""Validate the first-call asset/table initializer at 0x8d170."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_8d170_asset_table_initializer.c"


class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "paired_source_a", "paired_source_b", "paired_destination_a", "paired_destination_b",
        "paired_bytes", "paired_helper", "paired_upload_count", "fixed_source_a", "fixed_source_b",
        "fixed_destination_a", "fixed_destination_b", "fixed_bytes", "fixed_upload_count",
        "indexed_source_a", "indexed_source_b", "indexed_destination_a", "indexed_destination_b",
        "indexed_bytes", "indexed_helper", "indexed_upload_count", "indexed_stride", "indexed_limit",
        "table_a", "table_b", "table_stride", "table_limit", "table_sentinel",
        "table_write_offset_a", "table_write_offset_b")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "initializer.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8d170_asset_table_initializer
        fn.argtypes = [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        result = Result()
        assert fn(ctypes.byref(result)) == 1
        assert (result.paired_source_a, result.paired_source_b) == (0x51d5f0, 0x5289f0)
        assert (result.paired_destination_a, result.paired_destination_b) == (0x503ad0, 0x5040d0)
        assert (result.paired_bytes, result.paired_helper, result.paired_upload_count) == (0x600, 0xf5d40, 30)
        assert (result.fixed_source_a, result.fixed_source_b) == (0x560df0, 0x561370)
        assert (result.fixed_destination_a, result.fixed_destination_b) == (0x565320, 0x5658a0)
        assert (result.fixed_bytes, result.fixed_upload_count) == (0x580, 2)
        assert (result.indexed_source_a, result.indexed_source_b) == (0x533df0, 0x54a5f0)
        assert (result.indexed_destination_a, result.indexed_destination_b) == (0x503cd0, 0x5042d0)
        assert (result.indexed_bytes, result.indexed_helper, result.indexed_upload_count) == (0x400, 0xf5d40, 90)
        assert (result.indexed_stride, result.indexed_limit) == (0x400, 90)
        assert (result.table_a, result.table_b, result.table_stride, result.table_limit) == (0x5618f0, 0x561e90, 12, 90)
        assert (result.table_sentinel, result.table_write_offset_a, result.table_write_offset_b) == (0xffff, 4, 8)
    print("PASS: 0x8d170 asset/table initializer")


if __name__ == "__main__":
    main()
