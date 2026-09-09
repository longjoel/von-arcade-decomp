#!/usr/bin/env python3
"""Vectors for the 0x88e4c state-packet suffix."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_88e4c_state_packet.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "computed_word", "state_51c948", "computed_g7", "fifo_response", "record_30",
        "state_51c94c", "state_51c944", "packet_10_0", "packet_10_1", "packet_10_2",
        "fifo_address", "branch_target", "packet_command")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"88e4c:.*mov.*10,r13", r"88e50:.*ld.*0x51c948",
                        r"88e58:.*st.*r13,0x884000", r"88e68:.*st.*g6,0x884000",
                        r"88e70:.*st.*g4,0x884000", r"88e78:.*ld.*0x884000",
                        r"88e80:.*ldos.*0x30\(r11\)", r"88e84:.*st.*g7,0x51c94c",
                        r"88e90:.*stos.*g5,0x51c944", r"88e98:.*be.*0x89ad8",
                        r"88e9c:.*b.*0x89ac8"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "packet.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_88e4c_state_packet
        function.argtypes = [ctypes.c_uint32] * 5
        function.restype = Result
        result = function(0x40100000, 0x42a00000, 0x40200000, 0x12345678, 0)
        assert (result.state_51c94c, result.state_51c944,
                result.packet_10_0, result.packet_10_1, result.packet_10_2,
                result.branch_target) == (0x40200000, 0x12345678, 10,
                                           0x42a00000, 0x40100000, 0x89ad8)
        result = function(1, 2, 3, 4, 5)
        assert result.branch_target == 0x89ac8
        assert (result.fifo_address, result.packet_command) == (0x884000, 10)
    print("recovered 0x88e4c state-packet vectors: ok")


if __name__ == "__main__":
    main()
