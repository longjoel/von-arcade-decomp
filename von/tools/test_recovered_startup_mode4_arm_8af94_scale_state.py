#!/usr/bin/env python3
"""Vectors for selector-2 scale/state boundary at 0x8af94."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8af94_scale_state.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "selected_float", "scale_result", "positive_packet_word",
        "nonpositive_packet_word", "state_51c948", "state_51c94c", "positive_path",
        "state_continuation", "positive_continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8af94:.*ld.*0x51c984", r"8afd0:.*subr.*g4,g5,g5",
                        r"8afdc:.*mulr.*g5,g7,g5", r"8afe4:.*divr.*g4,g5,g4",
                        r"8afec:.*st.*g7,0x51c948",
                        r"8affc:.*cmpr.*0f0.0,g4", r"8b000:.*bge.*0x8b080",
                        r"8b06c:.*st.*g4,0x51c94c", r"8b074:.*st.*g6,0x51c948",
                        r"8b07c:.*b.*0x8b0b0", r"8b0a8:.*st.*g4,0x51c94c",
                        r"8b0b0:.*mov.*29,r12"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "scale.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8af94_scale_state
        function.argtypes = [ctypes.c_uint32] * 5
        function.restype = Result
        positive = function(0x3fc00000, 0x40000000, 0x1234, 0x5678, 1)
        assert (positive.state_51c948, positive.state_51c94c,
                positive.positive_continuation, positive.state_continuation) == (
                    0x40000000, 0x1234, 0x8b004, 0x8b0b0)
        nonpositive = function(0, 0x10, 0x1234, 0x5678, 0)
        assert (nonpositive.state_51c94c, nonpositive.positive_continuation) == (
            0x5678, 0x8b080)
    print("recovered 0x8af94 scale/state vectors: ok")


if __name__ == "__main__":
    main()
