#!/usr/bin/env python3
"""Vectors for the 0x8903c command-29/30/31 packet prefix."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8903c_packet_prefix.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "record_184", "record_8", "record_10", "table_word_10", "table_word_18",
        "first_fifo_response", "second_fifo_response", "transformed_record_184",
        "derived_first_word", "derived_difference", "packet_29_0", "packet_29_1",
        "packet_29_2", "packet_30_0", "packet_30_1", "packet_30_2", "packet_31_0",
        "packet_31_1", "packet_31_2", "packet_31_3", "packet_31_4", "packet_31_5",
        "packet_31_6", "fifo_address", "float_constant", "first_command",
        "second_command", "third_command", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8903c:.*ldos.*0x184\(g0\)", r"89040:.*mov.*29,r13",
                        r"8904c:.*lda.*0x42a00000", r"89054:.*st.*g6,0x51c948",
                        r"89064:.*ld.*0x8\(r10\)", r"89070:.*ld.*0x10\(r10\)",
                        r"89074:.*lda.*0xffffa000\(g4\)", r"8907c:.*and.*g13,g4,g1",
                        r"89090:.*st.*g6,0x884000", r"890a8:.*ld.*0x884000",
                        r"890b0:.*ld.*0x8\(g0\)", r"890b4:.*mov.*30,r12",
                        r"890c0:.*st.*g1,0x884000", r"890c8:.*st.*g6,0x884000",
                        r"890d0:.*ld.*0x884000", r"890d8:.*addr.*g7,g4,g7",
                        r"890dc:.*ld.*0x10\(g0\)", r"890e0:.*mov.*31,r13",
                        r"890ec:.*st.*g7,0x884000", r"89100:.*subr.*g6,g4,g1",
                        r"89114:.*st.*g7,0x51c950", r"8912c:.*st.*g1,0x51c954",
                        r"89134:.*ld.*0x884000"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8903c_packet_prefix
        function.argtypes = [ctypes.c_uint32] * 7
        function.restype = Result
        result = function(0x6123, 0x30, 0x500, 0x111, 0x222, 0x40, 0x60)
        assert (result.transformed_record_184, result.derived_first_word,
                result.derived_difference) == (0x123, 0x70, 0x4a0)
        assert (result.packet_29_0, result.packet_29_1, result.packet_29_2,
                result.packet_30_0, result.packet_30_1, result.packet_30_2) == (
                    29, 0x123, 0x42a00000, 30, 0x123, 0x42a00000)
        assert (result.packet_31_0, result.packet_31_1, result.packet_31_2,
                result.packet_31_3, result.packet_31_4, result.packet_31_5,
                result.packet_31_6) == (31, 0x70, 0x111, 0, 0, 0x4a0, 0x222)
        assert (result.fifo_address, result.first_command, result.second_command,
                result.third_command, result.continuation) == (0x884000, 29, 30, 31, 0x89178)
    print("recovered 0x8903c packet-prefix vectors: ok")


if __name__ == "__main__":
    main()
