#!/usr/bin/env python3
"""Vectors for the 0x8b754 selector-0 packet/state prefix."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8b754_packet_state_prefix.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [
        (name, ctypes.c_uint32) for name in (
            "first_response", "transformed_base", "masked_operand", "packet_float_word",
            "second_response", "current_record_8", "current_record_10")
    ] + [
        ("command_29_packet", ctypes.c_uint32 * 3),
        ("command_30_packet", ctypes.c_uint32 * 3),
    ] + [
        (name, ctypes.c_uint32) for name in (
            "state_51c940", "state_51c948", "state_51c950", "state_51c954",
            "fifo_address", "command_29", "command_30", "continuation")
    ]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8b754:.*lda.*0x1000\(r7\)", r"8b75c:.*mov.*29,g8",
        r"8b768:.*lda.*0xffff,g4", r"8b770:.*and.*g2,g4,g4",
        r"8b77c:.*lda.*0x42200000,g6", r"8b78c:.*ld.*0x884000,g1",
        r"8b794:.*ld.*0x8\(g0\),g7", r"8b798:.*mov.*30,g9",
        r"8b7bc:.*ld.*0x10\(g0\),g4", r"8b7c0:.*addr.*g1,g7,g0",
        r"8b7c4:.*subr.*g5,g4,g1", r"8b7d0:.*stos.*g2,0x51c940",
        r"8b7d8:.*st.*g6,0x51c948", r"8b7e8:.*st.*g0,0x51c950",
        r"8b7f0:.*st.*g1,0x51c954"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8b754_packet_state_prefix
        function.argtypes = [ctypes.c_uint32] * 4
        function.restype = Result
        result = function(0x12345678, 0x100, 0x30, 0x220)
        assert (result.transformed_base, result.masked_operand, result.packet_float_word) == (0x12346678, 0x6678, 0x42200000)
        assert list(result.command_29_packet) == [29, 0x6678, 0x42200000]
        assert list(result.command_30_packet) == [30, 0x6678, 0x42200000]
        assert (result.state_51c940, result.state_51c948, result.state_51c950,
                result.state_51c954, result.continuation) == (0x12346678, 0x42200000, 0x130, 0x120, 0x8b7e0)
    print("recovered 0x8b754 packet/state-prefix vectors: ok")


if __name__ == "__main__":
    main()
