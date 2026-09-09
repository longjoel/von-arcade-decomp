#!/usr/bin/env python3
"""Vectors for the 0x8baf0 selector-1 helper selection."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8baf0_float_selection.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "timing_5770f0", "adjusted_timing", "low_timing_path", "helper_input_x",
        "helper_input_y", "helper_result", "selected_float", "adjusted_float",
        "timing_zero_path", "helper_call", "positive_fallback", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8baf0:.*ld.*0x5770f0", r"8baf8:.*subo.*3,g4,g4",
        r"8bafc:.*cmpobl.*1,g4,0x8bb34", r"8bb00:.*lda.*0x40\(fp\),g2",
        r"8bb04:.*lda.*0x42\(fp\),g3", r"8bb08:.*call.*0x6ece0",
        r"8bb10:.*mov.*0,g8", r"8bb14:.*lda.*0x408f4000,g9",
        r"8bb1c:.*cmprl.*fp0,g8", r"8bb28:.*lda.*0x41f00000,r12",
        r"8bb38:.*ld.*0x5770f0", r"8bb40:.*cmpibne.*0,g4,0x8bb60"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "selection.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8baf0_float_selection
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        normal = function(4, 0xbfc00000)
        assert (normal.adjusted_timing, normal.low_timing_path, normal.selected_float,
                normal.adjusted_float, normal.continuation) == (1, 0, 0xbfc00000, 0xbfc00000, 0x8bb60)
        fallback = function(0, 0x3fc00000)
        assert (fallback.adjusted_float, fallback.timing_zero_path) == (0x42020000, 1)
        low = function(2, 0)
        assert (low.adjusted_timing, low.low_timing_path) == (0xffffffff, 0)
    print("recovered 0x8baf0 float-selection vectors: ok")


if __name__ == "__main__":
    main()
