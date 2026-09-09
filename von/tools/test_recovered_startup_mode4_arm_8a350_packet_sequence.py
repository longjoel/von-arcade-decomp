#!/usr/bin/env python3
"""Vectors for the selector-2 0x8a350 packet sequence."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8a350_packet_sequence.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state_51c940", "state_51c948", "record_8", "record_10", "linked_record_8",
        "linked_record_10", "command_29_response", "command_30_response",
        "command_10_response", "command_29_packet_0", "command_29_packet_1",
        "command_29_packet_2", "command_30_packet_0", "command_30_packet_1",
        "command_30_packet_2", "command_10_packet_0", "command_10_packet_1",
        "command_10_packet_2", "command_31_packet_0", "command_31_packet_1",
        "command_31_packet_2", "command_31_packet_3", "command_31_packet_4",
        "command_31_packet_5", "command_31_packet_6", "command_29_operand",
        "command_31_first_word", "command_31_fifth_word", "fifo_address",
        "first_command", "second_command", "third_command", "fourth_command",
        "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8a350:.*mov.*29,r12", r"8a35c:.*ldos.*0x51c940",
                        r"8a364:.*ld.*0x51c948", r"8a36c:.*st.*g4,0x884000",
                        r"8a374:.*st.*g5,0x884000", r"8a37c:.*ld.*0x884000",
                        r"8a384:.*ld.*0x8\(r10\)", r"8a388:.*mov.*30,r13",
                        r"8a394:.*st.*g4,0x884000", r"8a39c:.*st.*g5,0x884000",
                        r"8a3a4:.*ld.*0x884000", r"8a3ac:.*ld.*0x10\(r10\)",
                        r"8a3b0:.*ld.*0x8\(r11\)", r"8a3b4:.*addr.*g1,g6,g1",
                        r"8a3b8:.*subr.*g4,g0,g0", r"8a3c0:.*ld.*0x8\(r11\)",
                        r"8a3c4:.*subr.*g0,g4,g4", r"8a3c8:.*ld.*0x10\(r11\)",
                        r"8a3cc:.*subr.*g5,g1,g5", r"8a3d8:.*mov.*10,r12",
                        r"8a3e4:.*st.*g4,0x884000", r"8a3ec:.*st.*g5,0x884000",
                        r"8a3f4:.*ld.*0x884000", r"8a3fc:.*mov.*31,r13",
                        r"8a408:.*st.*g1,0x884000", r"8a410:.*st.*g7,0x884000",
                        r"8a42c:.*st.*g0,0x884000", r"8a434:.*st.*g2,0x884000",
                        r"8a43c:.*ld.*0x884000"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "packets.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8a350_packet_sequence
        function.argtypes = [ctypes.c_uint32] * 9
        function.restype = Result
        result = function(0xd400, 0x3f800000, 0x300, 0x500, 0x700, 0x900,
                          0x40, 0x60, 0x80)
        assert (result.command_29_packet_0, result.command_29_packet_1,
                result.command_29_packet_2, result.command_30_packet_0,
                result.command_30_packet_1, result.command_30_packet_2) == (
                    29, 0xd400, 0x3f800000, 30, 0xd400, 0x3f800000)
        assert (result.command_10_packet_0, result.command_10_packet_1,
                result.command_10_packet_2) == (10, 0x460, 0xfffffc40)
        assert (result.command_31_packet_0, result.command_31_packet_1,
                result.command_31_packet_2, result.command_31_packet_3,
                result.command_31_packet_4, result.command_31_packet_5,
                result.command_31_packet_6) == (31, 0x340, 0x700, 0, 0, 0x4a0, 0x900)
        assert (result.fifo_address, result.first_command, result.second_command,
                result.third_command, result.fourth_command, result.continuation) == (
                    0x884000, 29, 30, 10, 31, 0x8a43c)
    print("recovered 0x8a350 packet-sequence vectors: ok")


if __name__ == "__main__":
    main()
