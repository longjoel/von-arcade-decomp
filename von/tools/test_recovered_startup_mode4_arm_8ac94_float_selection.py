#!/usr/bin/env python3
"""Vectors for selector-1 helper selection at 0x8ac94."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8ac94_float_selection.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "helper_input_x", "helper_input_y", "helper_result", "selected_float",
        "adjusted_float", "timing_5770f0", "timing_zero_path", "helper_call",
        "positive_fallback", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8ac94:.*bl.*0x8acd0", r"8aca4:.*call.*0x6ece0",
                        r"8acb8:.*cmprl.*fp0,r12", r"8acc0:.*ble.*0x8acd4",
                        r"8acc4:.*lda.*0x41f00000", r"8acd4:.*ld.*0x5770f0",
                        r"8acf0:.*addrl.*fp0,g4,g4", r"8ad00:.*ld.*0x8\(r10\)"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "selection.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8ac94_float_selection
        function.argtypes = [ctypes.c_uint32] * 4
        function.restype = Result
        result = function(0x10, 0x20, 0xbf800000, 0)
        assert (result.selected_float, result.adjusted_float, result.timing_zero_path,
                result.helper_call, result.continuation) == (
                    0xbf800000, 0x3fc00000, 1, 0x6ece0, 0x8ad00)
        positive = function(0x10, 0x20, 0x3f800000, 7)
        assert (positive.selected_float, positive.adjusted_float,
                positive.timing_zero_path) == (0x41f00000, 0x41f00000, 0)
    print("recovered 0x8ac94 float-selection vectors: ok")


if __name__ == "__main__":
    main()
