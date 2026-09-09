#!/usr/bin/env python3
"""Vectors for selector-3 packet/state sequence at 0x8a670."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8a670_packet_state.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "first_response", "state_51c948", "state_51c950", "state_51c954",
        "rolling_51c958", "rolling_51c95c", "rolling_51c960", "command_29_packet_0",
        "command_29_packet_1", "command_29_packet_2", "command_30_packet_0",
        "command_30_packet_1", "command_30_packet_2", "command_31_packet_0",
        "command_31_packet_1", "command_31_packet_2", "command_31_packet_3",
        "command_31_packet_4", "command_31_response", "state_51c940", "fifo_address",
        "command_10", "command_31", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8a670:.*mov.*29,r12", r"8a67c:.*ldos.*0x51c940",
                        r"8a684:.*ld.*0x51c948", r"8a694:.*st.*g4,0x884000",
                        r"8a6b0:.*mov.*30,r13", r"8a6cc:.*ld.*0x884000,r8",
                        r"8a738:.*divrl.*g4,fp1,g6", r"8a760:.*subr.*r8,g13,g13",
                        r"8a764:.*mov.*10,r12", r"8a770:.*st.*g3,0x51c950",
                        r"8a78c:.*st.*g13,0x51c954", r"8a79c:.*st.*g5,0x51c958",
                        r"8a7a8:.*st.*g1,0x51c95c", r"8a7b0:.*st.*g0,0x51c960",
                        r"8a7d0:.*mov.*31,r13", r"8a7dc:.*stos.*g4,0x51c940"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "packet.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8a670_packet_state
        function.argtypes = [ctypes.c_uint32] * 8
        function.restype = Result
        result = function(0x12345678, 0x12340000, 0x44, 0x55, 0x66, 0x77, 0x88,
                          0x99)
        assert (result.command_29_packet_0, result.command_29_packet_1,
                result.command_29_packet_2) == (29, 0, 0x44)
        assert (result.command_30_packet_0, result.command_30_packet_1,
                result.command_30_packet_2) == (30, 0, 0x44)
        assert (result.command_31_packet_0, result.command_31_packet_1,
                result.command_31_packet_2, result.command_31_packet_3,
                result.command_31_packet_4) == (31, 0x66, 0x77, 0x88, 0)
        assert (result.state_51c950, result.state_51c940, result.fifo_address,
                result.continuation) == (0x12345678, 0x99, 0x884000, 0x8a7e4)
    print("recovered 0x8a670 packet/state vectors: ok")


if __name__ == "__main__":
    main()
