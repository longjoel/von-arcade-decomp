#!/usr/bin/env python3
"""Vectors for selector-2 helper-result selection at 0x8a1c0."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8a1c0_float_selection.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state_51c950", "state_51c954", "helper_result", "selected_float", "helper_call",
        "timing_address", "timing_zero_path", "positive_fallback", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8a1c0:.*bl.*0x8a208", r"8a1c4:.*ld.*0x51c950",
                        r"8a1cc:.*ld.*0x51c954", r"8a1dc:.*call.*0x6ece0",
                        r"8a1f0:.*cmprl.*fp0,r12", r"8a1fc:.*lda.*0x41f00000",
                        r"8a20c:.*ld.*0x5770f0", r"8a214:.*cmpibne.*0,g4,0x8a234",
                        r"8a218:.*movr.*r9,fp0", r"8a228:.*addrl.*fp0,g4,g4",
                        r"8a230:.*movr.*fp0,r9", r"8a234:.*ld.*0x51c984"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "selection.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8a1c0_float_selection
        function.argtypes = [ctypes.c_uint32] * 4
        function.restype = Result
        negative = function(0x70, 0x80, 0xbf800000, 0)
        assert (negative.selected_float, negative.timing_zero_path,
                negative.helper_call, negative.continuation) == (0xbf800000, 1,
                                                                  0x6ece0, 0x8a234)
        positive = function(0x90, 0xa0, 0x3f800000, 7)
        assert (positive.selected_float, positive.positive_fallback,
                positive.timing_zero_path) == (0x41f00000, 0x41f00000, 0)
    print("recovered 0x8a1c0 float-selection vectors: ok")


if __name__ == "__main__":
    main()
