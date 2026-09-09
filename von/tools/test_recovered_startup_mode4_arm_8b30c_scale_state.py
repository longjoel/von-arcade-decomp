#!/usr/bin/env python3
"""Vectors for selector-3 scale/state boundary at 0x8b30c."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8b30c_scale_state.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "selected_float", "scale_result", "positive_packet_word",
        "nonpositive_packet_word", "state_51c948", "state_51c94c", "positive_path",
        "branch_target", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8b30c:.*ld.*0xc\(r10\)", r"8b318:.*ld.*0x51c948",
                        r"8b320:.*mulr.*g4,g7,g4", r"8b328:.*divr.*g5,g4,g4",
                        r"8b32c:.*cmpr.*g7,g4", r"8b338:.*cmpr.*0f0.0,g4",
                        r"8b33c:.*bge.*0x8b3a0", r"8b38c:.*st.*g4,0x51c94c",
                        r"8b394:.*st.*g6,0x51c948", r"8b39c:.*b.*0x8b3f4",
                        r"8b3a0:.*ld.*0x51c984", r"8b3ec:.*st.*g4,0x51c94c",
                        r"8b3f4:.*mov.*29,r12"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "scale.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8b30c_scale_state
        function.argtypes = [ctypes.c_uint32] * 5
        function.restype = Result
        positive = function(0x3fc00000, 0x40000000, 0x1234, 0x5678, 1)
        assert (positive.state_51c948, positive.state_51c94c,
                positive.branch_target, positive.continuation) == (
                    0x40000000, 0x1234, 0x8b004, 0x8b3f4)
        nonpositive = function(0, 0x10, 0x1234, 0x5678, 0)
        assert (nonpositive.state_51c94c, nonpositive.branch_target) == (0x5678, 0x8b080)
    print("recovered 0x8b30c scale/state vectors: ok")


if __name__ == "__main__":
    main()
