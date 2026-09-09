#!/usr/bin/env python3
"""Vectors for the 0x8c7f0 selector-3 helper-selection block."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8c7f0_float_selection.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "timing_5770f0", "adjusted_timing", "low_timing_path", "helper_result",
        "selected_float", "timing_zero_path", "first_adjusted_float",
        "adjusted_float", "helper_input_x", "helper_input_y", "helper_call",
        "positive_fallback", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8c7f0:.*subo.*3,g4,g4", r"8c7f4:.*cmpo.*1,g4",
        r"8c808:.*bl.*0x8c83c", r"8c814:.*call.*0x6ece0",
        r"8c820:.*lda.*0x408f4000,r9", r"8c828:.*cmprl.*fp0,r8",
        r"8c82c:.*ble.*0x8c840", r"8c830:.*lda.*0x41f00000,g0",
        r"8c83c:.*mov.*0,g0", r"8c840:.*ld.*0x5770f0,g4",
        r"8c848:.*cmpibne.*0,g4,0x8c868", r"8c854:.*lda.*0x40140000,g5",
        r"8c870:.*lda.*0x40200000,g5", r"8c880:.*movr.*fp0,g7"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "selection.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8c7f0_float_selection
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        nonzero = function(5, 0x3f800000)
        assert (nonzero.selected_float, nonzero.first_adjusted_float,
                nonzero.adjusted_float, nonzero.low_timing_path,
                nonzero.timing_zero_path) == (0x41f00000, 0x41f00000, 0x41f00000, 0, 0)
        zero = function(0, 0xbf800000)
        assert (zero.selected_float, zero.first_adjusted_float, zero.adjusted_float,
                zero.low_timing_path, zero.timing_zero_path) == (
                0xbf800000, 0x3fc00000, 0x40800000, 1, 1)
        assert (zero.helper_input_x, zero.helper_input_y, zero.helper_call,
                zero.positive_fallback, zero.continuation) == (0x40, 0x42, 0x6ece0,
                                                               0x41f00000, 0x8c840)
    print("recovered 0x8c7f0 float-selection vectors: ok")


if __name__ == "__main__":
    main()
