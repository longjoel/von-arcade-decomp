#!/usr/bin/env python3
"""Vectors for selector-0 prefix at 0x8a964."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8a964_packet_state_prefix.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "counter_51c984", "prior_response_base", "timing_delta", "packet_operand",
        "packet_float_word", "first_response", "second_response", "current_record_8",
        "current_record_10", "command_29_packet_0", "command_29_packet_1",
        "command_29_packet_2", "command_30_packet_0", "command_30_packet_1",
        "command_30_packet_2", "state_51c940", "state_51c942", "state_51c948",
        "state_51c950", "state_51c954", "fifo_address", "command_29", "command_30",
        "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8a964:.*ld.*0x51c984", r"8a96c:.*lda.*0xb4",
                        r"8a970:.*subo.*g6,r12,g6", r"8a974:.*cvtir.*g6,fp0",
                        r"8a994:.*lda.*0x1000\(g2\)", r"8a99c:.*mov.*29,r13",
                        r"8a9a8:.*stos.*g7,0x51c940", r"8a9b0:.*shlo.*8,g6,g6",
                        r"8a9b4:.*subo.*g6,g7,g7", r"8a9d0:.*st.*g4,0x884000",
                        r"8a9d8:.*st.*g0,0x884000", r"8a9e0:.*ld.*0x884000,g13",
                        r"8a9ec:.*mov.*30,r12", r"8aa08:.*ld.*0x884000,g2",
                        r"8aa14:.*stos.*g6,0x51c942", r"8aa1c:.*addr.*g13,g3,g13",
                        r"8aa20:.*subr.*g2,g5,g1", r"8aa2c:.*stos.*g7,0x51c940",
                        r"8aa34:.*st.*g0,0x51c948", r"8aa44:.*st.*g13,0x51c950",
                        r"8aa4c:.*st.*g1,0x51c954", r"8aa54:.*bl.*0x8aa90"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8a964_packet_state_prefix
        function.argtypes = [ctypes.c_uint32] * 8
        function.restype = Result
        result = function(0x78, 0x20000, 0x12345678, 0x40600000,
                          0x100, 0x500, 0x20, 0x80)
        assert (result.timing_delta, result.command_29_packet_0,
                result.command_29_packet_1, result.command_29_packet_2,
                result.command_30_packet_0, result.command_30_packet_1,
                result.command_30_packet_2) == (0x3c, 29, 0x5678, 0x40600000,
                                                  30, 0x5678, 0x40600000)
        assert (result.state_51c940, result.state_51c942, result.state_51c948,
                result.state_51c950, result.state_51c954, result.continuation) == (
                    0x12345678, 0x3c00, 0x40600000, 0x120, 0x480, 0x8aa54)
    print("recovered 0x8a964 packet/state-prefix vectors: ok")


if __name__ == "__main__":
    main()
