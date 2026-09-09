#!/usr/bin/env python3
"""Vectors for selector-0 floating/packet tail at 0x8aa54."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8aa54_float_packet_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "helper_result", "selected_float", "adjusted_float", "timing_5770f0",
        "first_packet_word_1", "first_packet_word_2", "second_response",
        "computed_float_word", "first_response", "record_30", "command_10_packet_0_0",
        "command_10_packet_0_1", "command_10_packet_0_2", "command_10_packet_1_0",
        "command_10_packet_1_1", "command_10_packet_1_2", "state_51c940",
        "state_51c944", "state_51c94c", "fifo_address", "command", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8aa54:.*bl.*0x8aa90", r"8aa58:.*mov.*g13,g0",
                        r"8aa64:.*call.*0x6ece0", r"8aa78:.*cmprl.*fp0,r12",
                        r"8aa80:.*ble.*0x8aa94", r"8aa84:.*lda.*0x41f00000",
                        r"8aa94:.*ld.*0x5770f0", r"8aab0:.*addrl.*fp0,g4,g4",
                        r"8aafc:.*mov.*10,r13", r"8ab10:.*st.*g6,0x884000",
                        r"8ab18:.*st.*g5,0x884000", r"8ab20:.*ld.*0x884000,g7",
                        r"8ab48:.*mov.*10,r12", r"8ab54:.*st.*r12,0x884000",
                        r"8ab64:.*st.*g6,0x884000", r"8ab6c:.*st.*g4,0x884000",
                        r"8ab74:.*ld.*0x884000,g5", r"8ab80:.*stos.*g7,0x51c940",
                        r"8ab88:.*st.*g0,0x51c94c", r"8ab90:.*cmpi.*g4,0",
                        r"8ab94:.*stos.*g5,0x51c944", r"8ab9c:.*be.*0x8b604",
                        r"8aba0:.*b.*0x8aecc"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8aa54_float_packet_tail
        function.argtypes = [ctypes.c_uint32] * 9
        function.restype = Result
        result = function(0xbf800000, 0, 0x11, 0x22, 0x66, 0x40600000, 0x55, 0,
                          0x77)
        assert (result.selected_float, result.adjusted_float,
                result.command_10_packet_0_0, result.command_10_packet_0_1,
                result.command_10_packet_0_2, result.command_10_packet_1_1,
                result.command_10_packet_1_2,
                result.state_51c940, result.state_51c944, result.state_51c94c,
                result.continuation) == (0xbf800000, 0x3fc00000, 10, 0x11, 0x22,
                0x77, 0x40600000, 0x55, 0x66, 0x40600000, 0x8b604)
        positive = function(0x3f800000, 7, 0, 0, 0, 0, 0, 3, 0x99)
        assert (positive.selected_float, positive.adjusted_float,
                positive.continuation) == (0x41f00000, 0x41f00000, 0x8aecc)
    print("recovered 0x8aa54 float/packet-tail vectors: ok")


if __name__ == "__main__":
    main()
