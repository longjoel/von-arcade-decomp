#!/usr/bin/env python3
"""Vectors for selector-2 response tail at 0x8b1a4."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8b1a4_response_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "command_31_response", "computed_packet_word", "first_command_10_response",
        "second_command_10_response", "record_30", "command_10_packet_0",
        "command_10_packet_1", "command_10_packet_2", "state_51c940", "state_51c944",
        "state_51c950", "state_51c954", "fifo_address", "command", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8b1a4:.*ld.*0xc\(r11\)", r"8b1a8:.*movr.*g6,fp0",
                        r"8b1c4:.*st.*g1,0x51c950", r"8b1cc:.*st.*g0,0x51c954",
                        r"8b1d4:.*stos.*g5,0x51c940", r"8b1dc:.*st.*r12,0x884000",
                        r"8b1ec:.*st.*g3,0x884000", r"8b1f4:.*st.*g6,0x884000",
                        r"8b1fc:.*ld.*0x884000,g5", r"8b204:.*ldos.*0x30\(r11\)",
                        r"8b20c:.*stos.*g5,0x51c944", r"8b214:.*bne.*0x8b604",
                        r"8b218:.*b.*0x8aecc"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8b1a4_response_tail
        function.argtypes = [ctypes.c_uint32] * 7
        function.restype = Result
        zero = function(0x99, 0x40600000, 0x55, 0x66, 0x70, 0x80, 0)
        assert (zero.command_10_packet_0, zero.command_10_packet_1,
                zero.command_10_packet_2, zero.state_51c940, zero.state_51c944,
                zero.state_51c950, zero.state_51c954, zero.continuation) == (
                    10, 0x55, 0x40600000, 0x99, 0x66, 0x70, 0x80, 0x8aecc)
        nonzero = function(0x77, 0x1234, 0x11, 0x22, 0x90, 0xa0, 3)
        assert (nonzero.command, nonzero.fifo_address, nonzero.continuation) == (
            10, 0x884000, 0x8b604)
    print("recovered 0x8b1a4 response-tail vectors: ok")


if __name__ == "__main__":
    main()
