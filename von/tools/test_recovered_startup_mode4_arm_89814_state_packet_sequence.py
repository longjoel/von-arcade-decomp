#!/usr/bin/env python3
"""Vectors for the selector-5 0x89814 packet/state sequence."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_89814_state_packet_sequence.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "record_8", "record_10", "record_0c", "prior_51c958", "prior_51c95c", "prior_51c960",
        "first_fifo_response", "computed_second_command_word", "second_fifo_response",
        "first_command_packet_0", "first_command_packet_1", "first_command_packet_2",
        "command_31_packet_0", "command_31_packet_1", "command_31_packet_2",
        "command_31_packet_3", "command_31_packet_4", "command_31_packet_5",
        "command_31_packet_6", "second_command_packet_0", "second_command_packet_1",
        "second_command_packet_2", "state_51c940", "state_51c944", "state_51c94c",
        "state_51c950", "state_51c954", "fifo_address", "first_command", "second_command",
        "third_command", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"89814:.*ld.*0x10\(r10\)", r"89818:.*ld.*0x8\(r10\)",
                        r"8981c:.*mov.*10,r12", r"89828:.*ld.*0x51c960",
                        r"89830:.*ld.*0x51c958", r"89838:.*subr.*g2,g4,g4",
                        r"89844:.*subr.*g5,g1,g5", r"89850:.*st.*g4,0x884000",
                        r"89858:.*st.*g5,0x884000", r"89860:.*ld.*0x884000",
                        r"89868:.*mov.*31,r13", r"89874:.*st.*g1,0x884000",
                        r"8987c:.*st.*g6,0x884000", r"89890:.*st.*g4,0x884000",
                        r"898a0:.*st.*g3,0x884000", r"898ac:.*ld.*0x884000",
                        r"898d0:.*st.*g13,0x51c94c", r"898d8:.*st.*g1,0x51c950",
                        r"898e0:.*st.*r12,0x884000", r"898f0:.*st.*r6,0x884000",
                        r"898f8:.*st.*g6,0x884000", r"89900:.*ld.*0x884000",
                        r"8990c:.*st.*g2,0x51c954", r"89914:.*stos.*r4,0x51c940",
                        r"89920:.*st.*g5,0x51c944", r"8992c:.*b.*0x89ad8"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "sequence.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_89814_state_packet_sequence
        function.argtypes = [ctypes.c_uint32] * 9
        function.restype = Result
        result = function(0x300, 0x500, 0x111, 0x222, 0x333, 0x40, 0x40, 0x60, 0x42a00000)
        assert (result.first_command_packet_0, result.first_command_packet_1,
                result.first_command_packet_2) == (10, 0x1cd, 0x1ef)
        assert (result.command_31_packet_0, result.command_31_packet_1,
                result.command_31_packet_2, result.command_31_packet_3,
                result.command_31_packet_4, result.command_31_packet_5,
                result.command_31_packet_6) == (31, 0x111, 0x300, 0, 0, 0x333, 0x500)
        assert (result.computed_second_command_word,
                result.second_command_packet_0, result.second_command_packet_1,
                result.second_command_packet_2) == (0x1e2, 10, 0x42a00000, 0x1e2)
        assert (result.state_51c940, result.state_51c944, result.state_51c94c,
                result.state_51c950, result.state_51c954, result.fifo_address,
                result.continuation) == (0x40, 0x60, 0x222, 0x111, 0x333,
                                          0x884000, 0x89930)
    print("recovered 0x89814 state/packet-sequence vectors: ok")


if __name__ == "__main__":
    main()
