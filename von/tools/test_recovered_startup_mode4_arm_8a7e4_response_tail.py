#!/usr/bin/env python3
"""Vectors for selector-3 response tail at 0x8a7e4."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8a7e4_response_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "command_31_response", "computed_packet_word", "first_command_10_response",
        "second_command_10_response", "record_30", "command_10_packet_0",
        "command_10_packet_1", "command_10_packet_2", "state_51c940", "state_51c944",
        "fifo_address", "command", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8a7e4:.*st.*g3,0x884000", r"8a7ec:.*ld.*0x51c94c",
                        r"8a800:.*st.*g5,0x884000", r"8a810:.*subrl.*g6,fp0,g6",
                        r"8a82c:.*st.*g13,0x884000", r"8a83c:.*ld.*0x884000,g3",
                        r"8a844:.*st.*r12,0x884000", r"8a854:.*st.*g3,0x884000",
                        r"8a85c:.*st.*g6,0x884000", r"8a864:.*ld.*0x884000,g5",
                        r"8a86c:.*ldos.*0x30\(r11\)", r"8a874:.*stos.*g5,0x51c944",
                        r"8a87c:.*be.*0x8a16c"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8a7e4_response_tail
        function.argtypes = [ctypes.c_uint32] * 5
        function.restype = Result
        zero_record = function(0x99, 0x40600000, 0x55, 0x66, 0)
        assert (zero_record.command_10_packet_0, zero_record.command_10_packet_1,
                zero_record.command_10_packet_2, zero_record.state_51c940,
                zero_record.state_51c944, zero_record.continuation) == (
                    10, 0x55, 0x40600000, 0x99, 0x66, 0x8a16c)
        nonzero_record = function(0x77, 0xffffff80, 0x11, 0x22, 3)
        assert (nonzero_record.command, nonzero_record.fifo_address,
                nonzero_record.continuation) == (10, 0x884000, 0x8a880)
    print("recovered 0x8a7e4 response-tail vectors: ok")


if __name__ == "__main__":
    main()
