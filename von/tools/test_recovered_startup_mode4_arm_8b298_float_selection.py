#!/usr/bin/env python3
"""Vectors for selector-3 helper selection at 0x8b298."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8b298_float_selection.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state_51c950", "state_51c954", "helper_result", "selected_float",
        "adjusted_float", "timing_5770f0", "timing_zero_path", "helper_call",
        "positive_fallback", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8b298:.*bl.*0x8b2e0", r"8b2b4:.*call.*0x6ece0",
                        r"8b2c8:.*cmprl.*fp0,r12", r"8b2d0:.*ble.*0x8b2e4",
                        r"8b2d4:.*lda.*0x41f00000", r"8b2e4:.*ld.*0x5770f0",
                        r"8b300:.*addrl.*fp0,g4,g4", r"8b30c:.*ld.*0xc\(r10\)"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "selection.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8b298_float_selection
        function.argtypes = [ctypes.c_uint32] * 4
        function.restype = Result
        result = function(0x11, 0x22, 0xbf800000, 0)
        assert (result.selected_float, result.adjusted_float, result.timing_zero_path,
                result.helper_call, result.continuation) == (
                    0xbf800000, 0x3fc00000, 1, 0x6ece0, 0x8b30c)
        positive = function(0x11, 0x22, 0x3f800000, 7)
        assert (positive.selected_float, positive.adjusted_float,
                positive.timing_zero_path) == (0x41f00000, 0x41f00000, 0)
    print("recovered 0x8b298 float-selection vectors: ok")


if __name__ == "__main__":
    main()
