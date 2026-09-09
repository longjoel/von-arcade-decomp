#!/usr/bin/env python3
"""Vectors for selector-2 post-dispatch prefix at 0x8aed8."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8aed8_packet_state_prefix.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "timing_5770f0", "counter_51c984", "prior_response_base", "timing_delta",
        "transformed_base", "state_51c940", "state_51c942", "helper_input_x",
        "helper_input_y", "helper_call", "fifo_address", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8aed8:.*ld.*0x5770f0", r"8aee0:.*lda.*0x1000\(g2\)",
                        r"8aee8:.*ld.*0x51c984", r"8aef0:.*lda.*0xb4",
                        r"8aef4:.*stos.*g6,0x51c940", r"8aefc:.*subo.*3,g4,g4",
                        r"8af04:.*subo.*g5,r13,g5", r"8af08:.*shlo.*8,g5,g5",
                        r"8af10:.*stos.*g5,0x51c942", r"8af18:.*stos.*g6,0x51c940",
                        r"8af20:.*bl.*0x8af68"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8aed8_packet_state_prefix
        function.argtypes = [ctypes.c_uint32] * 5
        function.restype = Result
        result = function(7, 0x78, 0x20000, 0x55, 0x66)
        assert (result.timing_delta, result.transformed_base, result.state_51c940,
                result.state_51c942, result.helper_input_x, result.helper_input_y,
                result.continuation) == (0x3c, 0x1d400, 0x1d400, 0x3c00,
                                          0x55, 0x66, 0x8af20)
    print("recovered 0x8aed8 packet/state-prefix vectors: ok")


if __name__ == "__main__":
    main()
