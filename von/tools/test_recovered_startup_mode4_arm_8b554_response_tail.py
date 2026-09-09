#!/usr/bin/env python3
"""Vectors for selector-3 response tail at 0x8b554."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8b554_response_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "command_31_response", "computed_packet_word", "first_command_10_response",
        "second_command_10_response", "record_30", "command_10_packet_0",
        "command_10_packet_1", "command_10_packet_2", "state_51c940", "state_51c944",
        "fifo_address", "command", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8b554:.*mov.*31,r13", r"8b560:.*stos.*g4,0x51c940",
                        r"8b570:.*ld.*0x51c94c", r"8b5c8:.*st.*r12,0x884000",
                        r"8b5d8:.*st.*g3,0x884000", r"8b5e0:.*st.*g6,0x884000",
                        r"8b5e8:.*ld.*0x884000,g5", r"8b5f0:.*ldos.*0x30\(r11\)",
                        r"8b5f8:.*stos.*g5,0x51c944", r"8b600:.*be.*0x8aecc",
                        r"8b604:.*mov.*1,r12", r"8b608:.*st.*r12,0x51c9b4"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8b554_response_tail
        function.argtypes = [ctypes.c_uint32] * 5
        function.restype = Result
        zero = function(0x99, 0x40600000, 0x55, 0x66, 0)
        assert (zero.command_10_packet_0, zero.command_10_packet_1,
                zero.command_10_packet_2, zero.state_51c940, zero.state_51c944,
                zero.continuation) == (10, 0x55, 0x40600000, 0x99, 0x66, 0x8aecc)
        nonzero = function(0x77, 0x1234, 0x11, 0x22, 3)
        assert (nonzero.fifo_address, nonzero.continuation) == (0x884000, 0x8b604)
    print("recovered 0x8b554 response-tail vectors: ok")


if __name__ == "__main__":
    main()
