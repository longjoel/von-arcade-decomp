#!/usr/bin/env python3
"""Vectors for the 0x88d04 command-29/30 packet prefix."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_88d04_packet_prefix.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "record_184", "transformed_record_184", "fifo_response", "record_8",
        "packet_29_0", "packet_29_1", "packet_29_2", "packet_30_0",
        "packet_30_1", "packet_30_2", "fifo_address", "float_constant",
        "first_command", "second_command", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"88d04:.*ldos.*0x184\(g0\)", r"88d08:.*mov.*29,r13",
                        r"88d1c:.*lda.*0xffffa000\(g7\)", r"88d24:.*and.*g4,g7,g4",
                        r"88d30:.*lda.*0x42a00000", r"88d40:.*ld.*0x884000",
                        r"88d48:.*ld.*0x8\(g0\)", r"88d4c:.*mov.*30,r12",
                        r"88d58:.*st.*g4,0x884000", r"88d60:.*st.*g5,0x884000",
                        r"88d70:.*ld.*0x10\(g0\)"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_88d04_packet_prefix
        function.argtypes = [ctypes.c_uint32] * 3
        function.restype = Result
        result = function(0x6123, 0xdeadbeef, 0x1234)
        assert (result.transformed_record_184, result.packet_29_0,
                result.packet_29_1, result.packet_29_2,
                result.packet_30_0, result.packet_30_1, result.packet_30_2) == (
                    0x123, 29, 0x123, 0x42a00000, 30, 0x123, 0x42a00000)
        assert (result.fifo_address, result.float_constant,
                result.first_command, result.second_command, result.continuation) == (
                    0x884000, 0x42a00000, 29, 30, 0x88d70)
    print("recovered 0x88d04 packet-prefix vectors: ok")


if __name__ == "__main__":
    main()
