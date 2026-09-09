#!/usr/bin/env python3
"""Vectors for the 0x8c358 selector-1 helper selection."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8c358_float_selection.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "timing_5770f0", "adjusted_timing", "low_timing_path", "helper_result",
        "selected_float", "adjusted_float", "timing_zero_path", "helper_input_x",
        "helper_input_y", "helper_call", "positive_fallback", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8c358:.*subo.*3,g4,g4", r"8c35c:.*cmpo.*1,g4",
        r"8c370:.*bl.*0x8c3a4", r"8c374:.*lda.*0x40\(fp\),g2",
        r"8c378:.*lda.*0x42\(fp\),g3", r"8c37c:.*call.*0x6ece0",
        r"8c384:.*mov.*0,r8", r"8c388:.*lda.*0x408f4000,r9",
        r"8c390:.*cmprl.*fp0,r8", r"8c398:.*lda.*0x41f00000,g0",
        r"8c3a8:.*ld.*0x5770f0", r"8c3b0:.*cmpibne.*0,g4,0x8c3d0"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "selection.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8c358_float_selection
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        normal = function(4, 0xbfc00000)
        assert (normal.adjusted_timing, normal.low_timing_path, normal.selected_float,
                normal.adjusted_float, normal.continuation) == (1, 0, 0xbfc00000, 0xbfc00000, 0x8c3d0)
        fallback = function(0, 0x3fc00000)
        assert (fallback.selected_float, fallback.adjusted_float, fallback.timing_zero_path) == (0x41f00000, 0x42020000, 1)
    print("recovered 0x8c358 float-selection vectors: ok")


if __name__ == "__main__":
    main()
