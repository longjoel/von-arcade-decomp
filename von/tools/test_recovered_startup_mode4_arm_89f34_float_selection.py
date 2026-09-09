#!/usr/bin/env python3
"""Vectors for selector-1 helper-result selection at 0x89f34."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_89f34_float_selection.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "helper_input_x", "helper_input_y", "helper_result", "selected_float",
        "helper_call", "timing_address", "timing_zero_path", "positive_fallback",
        "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"89f34:.*bl.*0x89f70", r"89f38:.*mov.*g13,g0",
                        r"89f44:.*call.*0x6ece0", r"89f58:.*cmprl.*fp0,r12",
                        r"89f64:.*lda.*0x41f00000", r"89f74:.*ld.*0x5770f0",
                        r"89f7c:.*cmpibne.*0,g4,0x89f9c", r"89f80:.*movr.*r9,fp0",
                        r"89f90:.*addrl.*fp0,g4,g4", r"89f98:.*movr.*fp0,r9",
                        r"89f9c:.*ld.*0xc\(r10\)"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "selection.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_89f34_float_selection
        function.argtypes = [ctypes.c_uint32] * 4
        function.restype = Result
        negative = function(0x10, 0x20, 0xbf800000, 0)
        assert (negative.selected_float, negative.timing_zero_path,
                negative.helper_call, negative.timing_address, negative.continuation) == (
                    0xbf800000, 1, 0x6ece0, 0x5770f0, 0x89f9c)
        positive = function(0x30, 0x40, 0x3f800000, 7)
        assert (positive.selected_float, positive.positive_fallback,
                positive.timing_zero_path) == (0x41f00000, 0x41f00000, 0)
    print("recovered 0x89f34 float-selection vectors: ok")


if __name__ == "__main__":
    main()
