#!/usr/bin/env python3
"""Vectors for selector-3 packet/state builder at 0x8b3f4."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8b3f4_packet_state.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state_51c940", "state_51c948", "counter_51c984", "command_29_packet_0",
        "command_29_packet_1", "command_29_packet_2", "command_30_packet_0",
        "command_30_packet_1", "command_30_packet_2", "first_response",
        "second_response", "current_record_8", "current_record_10", "linked_record_8",
        "linked_record_10", "rolling_51c958", "rolling_51c95c", "rolling_51c960",
        "state_51c94c", "command_10", "fifo_address", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8b3f4:.*mov.*29,r12", r"8b400:.*ldos.*0x51c940",
                        r"8b408:.*ld.*0x51c948", r"8b410:.*ld.*0x51c984",
                        r"8b418:.*st.*g4,0x884000", r"8b430:.*ld.*0x8\(r10\)",
                        r"8b434:.*mov.*30,r13", r"8b440:.*st.*g4,0x884000",
                        r"8b448:.*st.*g6,0x884000", r"8b450:.*ld.*0x884000,r8",
                        r"8b4e8:.*mov.*10,r12", r"8b4f4:.*st.*g3,0x51c950",
                        r"8b510:.*st.*g13,0x51c954", r"8b520:.*st.*g5,0x51c958",
                        r"8b52c:.*st.*g1,0x51c95c", r"8b534:.*st.*g0,0x51c960",
                        r"8b544:.*st.*g4,0x884000"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "packet.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8b3f4_packet_state
        function.argtypes = [ctypes.c_uint32] * 13
        function.restype = Result
        result = function(0x12340000, 0x40600000, 0x95, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        assert (result.command_29_packet_0, result.command_29_packet_1,
                result.command_29_packet_2, result.command_30_packet_0,
                result.command_30_packet_1, result.command_30_packet_2,
                result.command_10, result.continuation) == (
                    29, 0, 0x40600000, 30, 0, 0x40600000, 10, 0x8b4e8)
        assert (result.rolling_51c958, result.rolling_51c95c,
                result.rolling_51c960, result.state_51c94c) == (7, 8, 9, 10)
    print("recovered 0x8b3f4 packet/state vectors: ok")


if __name__ == "__main__":
    main()
