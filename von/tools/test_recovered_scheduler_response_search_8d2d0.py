#!/usr/bin/env python3
"""Validate the normal cyclic search skeleton at 0x8d2d0."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_response_search_8d2d0.c"


class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "response_delta", "response_bias", "status_entry_count", "row_count",
        "initial_row", "attempts", "matched", "matched_row", "result_value",
        "low_response_target", "failure_result")]


class StatusResult(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "lower_threshold", "upper_threshold", "status_entry_count", "status_stride",
        "row_count", "row_stride", "initial_row", "attempts", "matched",
        "matched_row", "result_value", "failure_result")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "search.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_scheduler_response_search_8d2d0
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        rows = (ctypes.c_uint8 * 30)()
        rows[5] = 1
        result = Result()
        assert fn(5, 2, rows, ctypes.byref(result)) == 1
        assert (result.response_delta, result.initial_row, result.attempts,
                result.matched, result.matched_row, result.result_value) == (5, 3, 3, 1, 5, 28)
        rows = (ctypes.c_uint8 * 30)()
        assert fn(7, 29, rows, ctypes.byref(result)) == 1
        assert (result.attempts, result.matched, result.matched_row,
                result.result_value) == (30, 0, 30, 0xffffffff)
        rows = (ctypes.c_uint8 * 30)()
        rows[2] = 1
        assert fn(4, 0, rows, ctypes.byref(result)) == 1
        assert (result.matched, result.result_value) == (0, 0xffffffff)
        assert (result.status_entry_count, result.row_count,
                result.low_response_target) == (32, 30, 0x8d390)

        scan_fn = ctypes.CDLL(str(library)).recovered_scheduler_response_search_8d2d0_scan_status
        scan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(StatusResult)]
        scan_fn.restype = ctypes.c_int
        table = (ctypes.c_uint8 * (30 * 0x600))()
        slot = 5 * 0x600 + 2 * 0x20
        table[slot] = 50
        table[slot + 1] = 0
        status_result = StatusResult()
        assert scan_fn(10, 20, 3, table, ctypes.byref(status_result)) == 1
        assert (status_result.lower_threshold, status_result.upper_threshold,
                status_result.status_entry_count, status_result.status_stride,
                status_result.attempts, status_result.matched,
                status_result.matched_row, status_result.result_value) == (41, 51, 32, 0x20, 2, 1, 5, 29)
        table[slot + 1] = 1
        assert scan_fn(10, 20, 3, table, ctypes.byref(status_result)) == 1
        assert (status_result.matched, status_result.result_value) == (0, 0xffffffff)

        # The increment at 0x8d2dc wraps selector row 29 to row 0.
        rows = (ctypes.c_uint8 * 30)()
        rows[0] = 1
        assert fn(9, 29, rows, ctypes.byref(result)) == 1
        assert (result.initial_row, result.attempts, result.matched_row,
                result.result_value) == (0, 1, 0, 30)
    print("PASS: 0x8d2d0 response search")


if __name__ == "__main__":
    main()
