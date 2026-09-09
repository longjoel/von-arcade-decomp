#!/usr/bin/env python3
"""Vectors for the selector-2 0x8a178 packet/state prefix."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8a178_packet_state_prefix.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "timing_5770f0", "counter_51c984", "prior_fifo_response", "timing_minus_3",
        "timing_delta", "transformed_base", "state_51c940", "state_51c942",
        "fifo_address", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8a178:.*ld.*0x5770f0", r"8a180:.*lda.*0x1000\(g2\)",
                        r"8a188:.*ld.*0x51c984", r"8a190:.*lda.*0xb4",
                        r"8a194:.*stos.*g6,0x51c940", r"8a19c:.*subo.*3,g4,g4",
                        r"8a1a4:.*subo.*g5,r13,g5", r"8a1a8:.*shlo.*8,g5,g5",
                        r"8a1ac:.*subo.*g5,g6,g6", r"8a1b0:.*stos.*g5,0x51c942",
                        r"8a1b8:.*stos.*g6,0x51c940", r"8a1c0:.*bl.*0x8a208"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8a178_packet_state_prefix
        function.argtypes = [ctypes.c_uint32] * 3
        function.restype = Result
        result = function(7, 0x78, 0x20000)
        assert (result.timing_minus_3, result.timing_delta,
                result.transformed_base, result.state_51c940,
                result.state_51c942) == (4, 0x3c, 0x1d400, 0x1d400, 0x3c)
        assert (result.fifo_address, result.continuation) == (0x884000, 0x8a1c0)
    print("recovered 0x8a178 packet/state-prefix vectors: ok")


if __name__ == "__main__":
    main()
