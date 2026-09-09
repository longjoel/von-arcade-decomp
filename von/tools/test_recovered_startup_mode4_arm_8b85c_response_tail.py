#!/usr/bin/env python3
"""Vectors for the 0x8b85c selector-0 response tail."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8b85c_response_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [
        (name, ctypes.c_uint32) for name in (
            "packet_word_1", "packet_word_2", "computed_word", "first_response",
            "second_response", "state_51c948", "record_30")
    ] + [
        ("command_10_packet_0", ctypes.c_uint32 * 3),
        ("command_10_packet_1", ctypes.c_uint32 * 3),
    ] + [
        (name, ctypes.c_uint32) for name in (
            "state_51c940", "state_51c944", "state_51c94c", "fifo_address",
            "command", "continuation")
    ]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8b85c:.*ld.*0xc\(r14\),g4", r"8b870:.*ld.*0x10\(r13\),g6",
        r"8b874:.*ld.*0x51c954,g7", r"8b87c:.*ld.*0x51c950,g5",
        r"8b894:.*subr.*g7,g6,g6", r"8b898:.*subr.*g4,g5,g5",
        r"8b89c:.*mov.*10,g9", r"8b8b0:.*st.*g6,0x884000",
        r"8b8b8:.*st.*g5,0x884000", r"8b8c0:.*ld.*0x884000,g7",
        r"8b8ec:.*ld.*0x51c948,g6", r"8b8e8:.*mov.*10,g8",
        r"8b904:.*st.*g6,0x884000", r"8b90c:.*st.*g4,0x884000",
        r"8b920:.*stos.*g7,0x51c940", r"8b928:.*st.*g0,0x51c94c",
        r"8b934:.*stos.*g5,0x51c944", r"8b93c:.*be.*0x8bfac",
        r"8b940:.*b.*0x8bd60"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = pathlib.Path(library)
        loaded = ctypes.CDLL(str(function)).recovered_startup_mode4_arm_8b85c_response_tail
        loaded.argtypes = [ctypes.c_uint32] * 7
        loaded.restype = Result
        zero = loaded(0x11, 0x22, 0x33, 0x100, 0x200, 0x42200000, 0)
        assert list(zero.command_10_packet_0) == [10, 0x11, 0x22]
        assert list(zero.command_10_packet_1) == [10, 0x42200000, 0x33]
        assert (zero.state_51c940, zero.state_51c944, zero.state_51c94c,
                zero.continuation) == (0x100, 0x200, 0, 0x8bfac)
        nonzero = loaded(1, 2, 3, 4, 5, 6, 0x30)
        assert nonzero.continuation == 0x8bd60
    print("recovered 0x8b85c response-tail vectors: ok")


if __name__ == "__main__":
    main()
