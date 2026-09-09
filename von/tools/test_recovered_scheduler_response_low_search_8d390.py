#!/usr/bin/env python3
"""Validate the low-response reverse row search at 0x8d390."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_response_low_search_8d390.c"


class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "high_byte", "column_offset", "row_count", "initial_row", "probes",
        "matched", "matched_row", "result_value", "table_base", "row_stride",
        "failure_result")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "search.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_scheduler_response_low_search_8d390
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        rows = (ctypes.c_uint8 * 30)(*([1] * 30))
        rows[27] = 0
        result = Result()
        assert fn(0x123, 0, rows, ctypes.byref(result)) == 1
        assert (result.high_byte, result.column_offset, result.initial_row,
                result.probes, result.matched, result.matched_row,
                result.result_value) == (0x23, 0x460, 0, 3, 1, 27, 3)
        rows = (ctypes.c_uint8 * 30)(*([1] * 30))
        assert fn(0, 4, rows, ctypes.byref(result)) == 1
        assert (result.probes, result.matched, result.matched_row,
                result.result_value) == (30, 0, 30, 0xffffffff)
        rows = (ctypes.c_uint8 * 30)(*([1] * 30))
        rows[3] = 0
        assert fn(0, 4, rows, ctypes.byref(result)) == 1
        assert (result.probes, result.matched_row, result.result_value) == (1, 3, 1)
        assert (result.table_base, result.row_stride, result.failure_result) == (0x51d7f0, 0x600, 0xffffffff)
    print("PASS: 0x8d390 low-response search")


if __name__ == "__main__":
    main()
