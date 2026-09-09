#!/usr/bin/env python3
"""Vectors for the 0x8c510 selector-1 command/response tail."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8c510_packet_state_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state_51c950", "rolling_51c958", "state_51c954", "rolling_51c960",
        "state_51c94c", "command_10_word_0", "command_10_word_1",
        "command_10_word_2", "command_10_word_3", "command_10_word_4",
        "first_response", "second_response", "marker_1d0", "record_30")]
    _fields_ += [(name, ctypes.c_uint32 * size) for name, size in (
        ("command_31_packet", 6), ("command_10_packet_0", 3),
        ("command_10_packet_1", 3))]
    _fields_ += [(name, ctypes.c_uint32) for name in (
        "state_51c940", "state_51c944", "selector_51c99c", "state_51c9b4",
        "fifo_address", "command_31", "command_10", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8c510:.*ld.*0x51c95c,g4", r"8c520:.*lda.*0x40240000,r9",
        r"8c52c:.*bge.*0x8c540", r"8c540:.*mov.*31,r8",
        r"8c54c:.*ld.*0x51c950,g0", r"8c55c:.*ld.*0x51c958,g2",
        r"8c56c:.*ld.*0x51c94c,g6", r"8c574:.*ld.*0x51c95c,g3",
        r"8c57c:.*st.*g0,0x884000", r"8c584:.*st.*g2,0x884000",
        r"8c5cc:.*mov.*10,r9", r"8c5d8:.*subrl.*fp0,g6,g6",
        r"8c5ec:.*mov.*10,r8", r"8c608:.*st.*g4,0x884000",
        r"8c610:.*st.*g6,0x884000", r"8c620:.*ldos.*0x1d0\(r4\),g4",
        r"8c624:.*stos.*g0,0x51c940", r"8c630:.*stos.*g5,0x51c944",
        r"8c638:.*bne.*0x8c648", r"8c640:.*st.*r8,0x51c99c",
        r"8c648:.*ldos.*0x30\(r5\),g4", r"8c64c:.*cmpibne.*0,g4,0x8c904"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8c510_packet_state_tail
        function.argtypes = [ctypes.c_uint32] * 14
        function.restype = Result
        zero = function(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0, 0)
        assert list(zero.command_31_packet) == [31, 1, 2, 0, 0, 3]
        assert list(zero.command_10_packet_0) == [10, 6, 7]
        assert list(zero.command_10_packet_1) == [10, 8, 9]
        assert (zero.state_51c940, zero.state_51c944, zero.selector_51c99c,
                zero.continuation) == (11, 12, 2, 0x8c90c)
        marker = function(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 1)
        assert (marker.selector_51c99c, marker.state_51c9b4, marker.continuation) == (1, 1, 0x8c90c)
        zero_marker = function(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0, 1)
        assert (zero_marker.selector_51c99c, zero_marker.state_51c9b4, zero_marker.continuation) == (2, 0, 0x8c90c)
    print("recovered 0x8c510 packet/state-tail vectors: ok")


if __name__ == "__main__":
    main()
