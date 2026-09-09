#!/usr/bin/env python3
"""Vectors for selector-2 response tail at 0x8a43c."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8a43c_response_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "command_31_response", "computed_base_float", "linked_record_0c",
        "prior_state_51c950", "prior_state_51c954", "first_command_10_response",
        "second_command_10_response", "record_30", "command_10_packet_0",
        "command_10_packet_1", "command_10_packet_2", "command_10_float_delta",
        "state_51c940", "state_51c944", "state_51c950", "state_51c954", "fifo_address",
        "command", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8a43c:.*ld.*0x884000", r"8a444:.*ld.*0xc\(r11\)",
                        r"8a448:.*movr.*g6,fp0", r"8a45c:.*movr.*g4,fp0",
                        r"8a460:.*subrl.*fp0,g6,g6", r"8a464:.*st.*g1,0x51c950",
                        r"8a46c:.*st.*g0,0x51c954", r"8a474:.*st.*g5,0x51c940",
                        r"8a47c:.*st.*r12,0x884000", r"8a48c:.*st.*g3,0x884000",
                        r"8a494:.*st.*g6,0x884000", r"8a49c:.*ld.*0x884000",
                        r"8a4a4:.*ldos.*0x30\(r11\)", r"8a4ac:.*stos.*g5,0x51c944",
                        r"8a4b4:.*bne.*0x8a880", r"8a4b8:.*b.*0x8a16c"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8a43c_response_tail
        function.argtypes = [ctypes.c_uint32] * 8
        function.restype = Result
        zero_record = function(0x99, 0x40800000, 0x3f000000, 0x70, 0x80,
                               0x55, 0x66, 0)
        assert (zero_record.command_10_packet_0, zero_record.command_10_packet_1,
                zero_record.command_10_packet_2) == (10, 0x99, 0x40600000)
        assert (zero_record.state_51c940, zero_record.state_51c944,
                zero_record.state_51c950, zero_record.state_51c954,
                zero_record.continuation) == (0x55, 0x66, 0x70, 0x80, 0x8a16c)
        nonzero_record = function(0x77, 0xbf800000, 0x3f000000, 0x90, 0xa0,
                                  0x11, 0x22, 3)
        assert (nonzero_record.command_10_float_delta,
                nonzero_record.state_51c940, nonzero_record.state_51c944,
                nonzero_record.continuation, nonzero_record.fifo_address) == (
                    0xbfc00000, 0x11, 0x22, 0x8a880, 0x884000)
    print("recovered 0x8a43c response-tail vectors: ok")


if __name__ == "__main__":
    main()
