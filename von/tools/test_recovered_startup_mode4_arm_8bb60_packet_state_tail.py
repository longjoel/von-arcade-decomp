#!/usr/bin/env python3
"""Vectors for the 0x8bb60 selector-1 packet/state tail."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8bb60_packet_state_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "command_31_word", "first_command_10_word_1", "first_command_10_word_2",
        "second_command_10_word_1", "second_command_10_word_2", "rolling_51c958",
        "rolling_51c95c", "rolling_51c960", "state_51c94c", "command_31_response",
        "first_command_10_response", "second_command_10_response", "record_30")]
    _fields_ += [(name, ctypes.c_uint32 * size) for name, size in (
        ("command_31_packet", 2), ("command_10_packet_0", 3),
        ("command_10_packet_1", 3))]
    _fields_ += [(name, ctypes.c_uint32) for name in (
        "state_51c940", "state_51c944", "fifo_address", "command_31",
        "command_10", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8bb60:.*ld.*0x8\(r14\),r10", r"8bb70:.*subr.*g5,g6,g6",
        r"8bb80:.*ld.*0x51c984,g4", r"8bba0:.*cvtir.*g4,fp1",
        r"8bbd0:.*divrl.*g0,r6,r6", r"8bbd4:.*divrl.*g0,r8,r8",
        r"8bc30:.*mov.*31,g9", r"8bc34:.*st.*g9,0x884000",
        r"8bc3c:.*st.*g13,0x884000", r"8bc6c:.*st.*g0,0x51c958",
        r"8bc74:.*st.*r4,0x51c95c", r"8bc9c:.*st.*g6,0x51c94c",
        r"8bcf4:.*mov.*10,g8", r"8bd04:.*st.*g1,0x884000",
        r"8bd0c:.*st.*g13,0x884000", r"8bd48:.*stos.*g7,0x51c940",
        r"8bd50:.*stos.*g4,0x51c944", r"8bd58:.*ldos.*0x30\(r14\),g4",
        r"8bd5c:.*cmpibne.*0,g4,0x8bfac"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8bb60_packet_state_tail
        function.argtypes = [ctypes.c_uint32] * 13
        function.restype = Result
        zero = function(0x11, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0)
        assert list(zero.command_31_packet) == [31, 0x11]
        assert list(zero.command_10_packet_0) == [10, 1, 2]
        assert list(zero.command_10_packet_1) == [10, 3, 4]
        assert (zero.state_51c940, zero.state_51c944, zero.continuation) == (10, 11, 0x8bd60)
        nonzero = function(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x30)
        assert nonzero.continuation == 0x8bfac
    print("recovered 0x8bb60 packet/state-tail vectors: ok")


if __name__ == "__main__":
    main()
