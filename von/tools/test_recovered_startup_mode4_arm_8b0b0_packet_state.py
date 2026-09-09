#!/usr/bin/env python3
"""Vectors for selector-2 packet/state sequence at 0x8b0b0."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8b0b0_packet_state.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state_51c940", "state_51c948", "state_51c94c", "command_29_packet_0",
        "command_29_packet_1", "command_29_packet_2", "command_30_packet_0",
        "command_30_packet_1", "command_30_packet_2", "command_10_packet_0",
        "command_10_packet_1", "command_10_packet_2", "command_31_packet_0",
        "command_31_packet_1", "command_31_packet_2", "command_31_packet_3",
        "command_31_packet_4", "command_31_packet_5", "first_response", "second_response",
        "command_10_response", "command_31_response", "state_51c950", "state_51c954",
        "rolling_51c958", "rolling_51c95c", "rolling_51c960", "fifo_address",
        "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8b0b0:.*mov.*29,r12", r"8b0bc:.*ldos.*0x51c940",
                        r"8b0c4:.*ld.*0x51c948", r"8b0cc:.*st.*g4,0x884000",
                        r"8b0e4:.*ld.*0x8\(r10\)", r"8b0e8:.*mov.*30,r13",
                        r"8b0f4:.*st.*g4,0x884000", r"8b0fc:.*st.*g5,0x884000",
                        r"8b104:.*ld.*0x884000,g4", r"8b114:.*addr.*g1,g6,g1",
                        r"8b130:.*ld.*0x51c94c", r"8b138:.*mov.*10,r12",
                        r"8b144:.*st.*g4,0x884000", r"8b14c:.*st.*g5,0x884000",
                        r"8b154:.*ld.*0x884000,g5", r"8b15c:.*mov.*31,r13",
                        r"8b168:.*st.*g1,0x884000", r"8b170:.*st.*g7,0x884000",
                        r"8b19c:.*ld.*0x884000,g3", r"8b1c4:.*st.*g1,0x51c950",
                        r"8b1cc:.*st.*g0,0x51c954", r"8b1d4:.*stos.*g5,0x51c940",
                        r"8b1f4:.*st.*g6,0x884000", r"8b204:.*ldos.*0x30\(r11\)"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "packet.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8b0b0_packet_state
        function.argtypes = [ctypes.c_uint32] * 19
        function.restype = Result
        result = function(0x12340000, 0x40600000, 0x10, 0x11, 0x22, 0x31, 0x32,
                          0x33, 0x34, 0x35, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        assert (result.command_29_packet_0, result.command_29_packet_1,
                result.command_29_packet_2, result.command_30_packet_0,
                result.command_30_packet_1, result.command_30_packet_2,
                result.command_10_packet_0, result.command_31_packet_0,
                result.command_31_packet_5, result.state_51c940,
                result.state_51c950, result.continuation) == (
                    29, 0, 0x40600000, 30, 0, 0x40600000, 10, 31, 0x35,
                    0x12340000, 5, 0x8b1a4)
    print("recovered 0x8b0b0 packet/state vectors: ok")


if __name__ == "__main__":
    main()
