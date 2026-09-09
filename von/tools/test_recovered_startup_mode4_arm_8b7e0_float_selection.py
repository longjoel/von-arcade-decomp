#!/usr/bin/env python3
"""Vectors for the 0x8b7e0 selector-0 helper selection."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8b7e0_float_selection.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "masked_operand", "adjusted_operand", "low_operand_path", "state_51c950",
        "state_51c954", "helper_input_x", "helper_input_y", "helper_result",
        "selected_float", "adjusted_float", "timing_5770f0", "timing_zero_path",
        "helper_call", "positive_fallback", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8b7e0:.*subo.*3,g4,g4", r"8b7e4:.*cmpo.*1,g4",
        r"8b7f8:.*bl.*0x8b830", r"8b7fc:.*lda.*0x40\(fp\),g2",
        r"8b800:.*lda.*0x42\(fp\),g3", r"8b804:.*call.*0x6ece0",
        r"8b80c:.*mov.*0,g8", r"8b810:.*lda.*0x408f4000,g9",
        r"8b818:.*cmprl.*fp0,g8", r"8b824:.*lda.*0x41f00000,r12",
        r"8b834:.*ld.*0x5770f0", r"8b83c:.*cmpibne.*0,g4,0x8b85c",
        r"8b848:.*lda.*0x40140000,g5", r"8b850:.*addrl.*fp0,g4,g4"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "selection.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8b7e0_float_selection
        function.argtypes = [ctypes.c_uint32] * 5
        function.restype = Result
        normal = function(0x6678, 0x130, 0x120, 0x3fc00000, 1)
        assert (normal.adjusted_operand, normal.low_operand_path, normal.selected_float,
                normal.adjusted_float, normal.helper_call, normal.continuation) == (0x6675, 0, 0x41f00000, 0x41f00000, 0x6ece0, 0x8b85c)
        fallback = function(0x6678, 0x130, 0x120, 0x3fc00000, 0)
        assert (fallback.adjusted_float, fallback.timing_zero_path) == (0x42020000, 1)
        low = function(2, 0, 0, 0, 1)
        assert (low.adjusted_operand, low.low_operand_path) == (0xffffffff, 1)
    print("recovered 0x8b7e0 float-selection vectors: ok")


if __name__ == "__main__":
    main()
