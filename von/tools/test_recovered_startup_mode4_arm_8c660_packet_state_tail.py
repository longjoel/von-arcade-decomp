#!/usr/bin/env python3
"""Vectors for the 0x8c660 selector-2 packet/state tail."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8c660_packet_state_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state_51c950", "rolling_51c958", "state_51c954", "rolling_51c960",
        "state_51c94c", "command_10_word_0", "command_10_word_1",
        "command_10_word_2", "command_10_word_3", "first_response",
        "second_response", "record_30")]
    _fields_ += [(name, ctypes.c_uint32 * size) for name, size in (
        ("command_31_packet", 6), ("command_10_packet_0", 3),
        ("command_10_packet_1", 3))]
    _fields_ += [(name, ctypes.c_uint32) for name in (
        "state_51c940", "state_51c944", "fifo_address", "command_31",
        "command_10", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8c660:.*mov.*31,r8", r"8c66c:.*ld.*0x51c950,g1",
        r"8c67c:.*ld.*0x51c958,g3", r"8c68c:.*ld.*0x51c94c,g6",
        r"8c694:.*ld.*0x51c95c,g13", r"8c69c:.*st.*g1,0x884000",
        r"8c6a4:.*st.*g3,0x884000", r"8c6c4:.*st.*g5,0x884000",
        r"8c6d8:.*subr.*g3,g1,g1", r"8c6ec:.*mov.*10,r9",
        r"8c6fc:.*st.*g5,0x884000", r"8c704:.*st.*g1,0x884000",
        r"8c70c:.*mov.*10,r8", r"8c728:.*st.*g4,0x884000",
        r"8c730:.*st.*g6,0x884000", r"8c740:.*ldos.*0x30\(g0\),g4",
        r"8c744:.*stos.*g1,0x51c940", r"8c750:.*stos.*g5,0x51c944",
        r"8c758:.*be.*0x8c8f4", r"8c75c:.*b.*0x8c904"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8c660_packet_state_tail
        function.argtypes = [ctypes.c_uint32] * 12
        function.restype = Result
        zero = function(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0)
        assert list(zero.command_31_packet) == [31, 1, 2, 0, 0, 3]
        assert list(zero.command_10_packet_0) == [10, 6, 7]
        assert list(zero.command_10_packet_1) == [10, 8, 9]
        assert (zero.state_51c940, zero.state_51c944, zero.continuation) == (10, 11, 0x8c8f4)
        nonzero = function(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 1)
        assert nonzero.continuation == 0x8c904
    print("recovered 0x8c660 packet/state-tail vectors: ok")


if __name__ == "__main__":
    main()
