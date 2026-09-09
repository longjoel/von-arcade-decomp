#!/usr/bin/env python3
"""Validate the deterministic selector prefix at 0x8d2a0."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_response_selector_8d2a0.c"


class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "counter", "modulo", "counter_remainder", "shifted_index", "capped_index",
        "response", "result_value", "special_response", "special_result",
        "special_return", "normal_continuation")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "selector.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_scheduler_response_selector_8d2a0
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        for counter in (0, 1, 119, 120, 121, 239, 240, 0xffffffff):
            for response in (10, 9):
                result = Result()
                assert fn(counter, response, ctypes.byref(result)) == 1
                remainder = counter % 120
                shifted = remainder >> 2
                assert (result.counter_remainder, result.shifted_index,
                        result.capped_index) == (remainder, shifted, min(shifted, 29))
                assert result.result_value == (10 if response == 10 else 0)
                assert (result.special_return, result.normal_continuation) == (0x8d3ec, 0x8d2d0)
    print("PASS: 0x8d2a0 response selector")


if __name__ == "__main__":
    main()
