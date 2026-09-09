#!/usr/bin/env python3
"""Vectors for the 0x8c0e0 selector-0 packet/state prefix."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8c0e0_packet_state_prefix.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "first_response", "transformed_base", "masked_operand", "second_response",
        "current_record_8", "current_record_10", "packet_float_word")]
    _fields_ += [(name, ctypes.c_uint32 * 3) for name in ("command_29_packet", "command_30_packet")]
    _fields_ += [(name, ctypes.c_uint32) for name in (
        "state_51c940", "state_51c948", "state_51c950", "state_51c954",
        "fifo_address", "command_29", "command_30", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8c0e0:.*lda.*0xffffa000\(g2\)", r"8c0e8:.*mov.*29,r9",
        r"8c0f4:.*lda.*0xffff,g4", r"8c0fc:.*and.*g2,g4,g4",
        r"8c108:.*lda.*0x42200000,g6", r"8c118:.*ld.*0x884000,g1",
        r"8c120:.*ld.*0x8\(g0\),g7", r"8c124:.*mov.*30,r8",
        r"8c140:.*ld.*0x884000,g5", r"8c148:.*ld.*0x10\(g0\),g4",
        r"8c14c:.*addr.*g1,g7,g0", r"8c15c:.*stos.*g2,0x51c940",
        r"8c164:.*st.*g6,0x51c948", r"8c174:.*st.*g0,0x51c950",
        r"8c17c:.*st.*g1,0x51c954"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8c0e0_packet_state_prefix
        function.argtypes = [ctypes.c_uint32] * 4
        function.restype = Result
        result = function(0x12345678, 0x100, 0x30, 0x220)
        assert (result.transformed_base, result.masked_operand, result.packet_float_word) == (0x1233f678, 0xf678, 0x42200000)
        assert list(result.command_29_packet) == [29, 0xf678, 0x42200000]
        assert list(result.command_30_packet) == [30, 0xf678, 0x42200000]
        assert (result.state_51c940, result.state_51c950, result.state_51c954,
                result.continuation) == (0x1233f678, 0x130, 0x120, 0x8c16c)
    print("recovered 0x8c0e0 packet/state-prefix vectors: ok")


if __name__ == "__main__":
    main()
