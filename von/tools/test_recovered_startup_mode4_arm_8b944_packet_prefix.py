#!/usr/bin/env python3
"""Vectors for the 0x8b944 selector-1 packet prefix."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8b944_packet_prefix.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "first_response", "transformed_base", "masked_operand",
        "followup_masked_operand", "packet_float_word")]
    _fields_ += [(name, ctypes.c_uint32 * 3) for name in (
        "command_29_packet", "command_30_packet", "followup_packet")]
    _fields_ += [(name, ctypes.c_uint32) for name in (
        "fifo_address", "command_29", "command_30", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8b944:.*lda.*0x1000\(r7\)", r"8b94c:.*mov.*29,g9",
        r"8b958:.*lda.*0xffff,g4", r"8b960:.*and.*r9,g4,g6",
        r"8b96c:.*lda.*0x42200000,g2", r"8b984:.*ld.*0x884000,g3",
        r"8b98c:.*ld.*0x8\(g0\),r6", r"8b990:.*mov.*30,g8",
        r"8b9ac:.*ld.*0x884000,r5", r"8b9b4:.*ld.*0x10\(g0\),g1",
        r"8b9b8:.*st.*g9,0x884000", r"8b9c0:.*lda.*0x5000\(r7\)",
        r"8b9c8:.*and.*g4,r7,g4", r"8b9d4:.*st.*g2,0x884000",
        r"8b9dc:.*ld.*0x884000,g13"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8b944_packet_prefix
        function.argtypes = [ctypes.c_uint32]
        function.restype = Result
        result = function(0x12345678)
        assert (result.transformed_base, result.masked_operand,
                result.followup_masked_operand, result.packet_float_word) == (0x12346678, 0x6678, 0xa678, 0x42200000)
        assert list(result.command_29_packet) == [29, 0x6678, 0x42200000]
        assert list(result.command_30_packet) == [30, 0x6678, 0x42200000]
        assert list(result.followup_packet) == [0x12346678, 0xa678, 0x42200000]
        assert result.continuation == 0x8b9e4
    print("recovered 0x8b944 packet-prefix vectors: ok")


if __name__ == "__main__":
    main()
