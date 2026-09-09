#!/usr/bin/env python3
"""Vectors for selector-1 packet/state tail at 0x8ad00."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8ad00_packet_state_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "command_31_first_word", "command_31_word_1", "command_31_word_2",
        "command_31_word_3", "command_31_word_4", "first_command_10_word_1",
        "first_command_10_word_2", "second_command_10_word_1",
        "second_command_10_word_2", "rolling_51c958", "rolling_51c95c",
        "rolling_51c960", "state_51c94c", "command_31_response",
        "first_command_10_response", "second_command_10_response", "record_30",
        "state_51c940", "state_51c944", "fifo_address", "command_31", "command_10",
        "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8ad00:.*ld.*0x8\(r10\)", r"8ad74:.*mov.*31,r13",
                        r"8ad94:.*st.*r13,0x884000", r"8add8:.*st.*g0,0x51c958",
                        r"8ade0:.*st.*g3,0x51c95c", r"8ae08:.*st.*g6,0x51c94c",
                        r"8ae48:.*st.*g6,0x51c960", r"8ae60:.*mov.*10,r12",
                        r"8ae70:.*st.*g1,0x884000", r"8ae78:.*st.*g2,0x884000",
                        r"8ae80:.*ld.*0x884000,g7", r"8ae88:.*mov.*10,r13",
                        r"8ae9c:.*st.*g3,0x884000", r"8aea4:.*st.*g4,0x884000",
                        r"8aeac:.*ld.*0x884000,g4", r"8aeb4:.*stos.*g7,0x51c940",
                        r"8aebc:.*stos.*g4,0x51c944", r"8aec4:.*ldos.*0x30\(r11\)",
                        r"8aec8:.*cmpibne.*0,.*0x8b604", r"8aecc:.*st.*g14,0x51c9b4"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8ad00_packet_state_tail
        function.argtypes = [ctypes.c_uint32] * 17
        function.restype = Result
        result = function(0x10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                          13, 14, 15, 0)
        assert (result.state_51c940, result.state_51c944, result.command_31,
                result.command_10, result.fifo_address, result.continuation) == (
                    14, 15, 31, 10, 0x884000, 0x8aecc)
        nonzero = function(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3)
        assert nonzero.continuation == 0x8b604
    print("recovered 0x8ad00 packet/state-tail vectors: ok")


if __name__ == "__main__":
    main()
