#!/usr/bin/env python3
"""Vectors for the selector-4 0x899d8 floating/state tail."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_899d8_float_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "helper_result", "record_0c", "prior_51c940", "state_51c948", "second_fifo_response",
        "record_30", "selected_float", "computed_command_word", "packet_10_0",
        "packet_10_1", "packet_10_2", "state_51c940", "state_51c944", "state_51c94c",
        "state_51c9b4", "helper_call", "fifo_address", "command", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"899d8:.*bl.*0x89a10", r"89a10:.*mov.*0,r9",
                        r"89a14:.*ld.*0x5770f0", r"89a1c:.*cmpibne.*0x89a3c",
                        r"89a3c:.*movr.*r9,fp0", r"89a44:.*lda.*0x40200000",
                        r"89a4c:.*addrl.*fp0,g4,g4", r"89a54:.*movr.*fp0,g7",
                        r"89a5c:.*ld.*0xc\(r10\)", r"89a6c:.*subrl.*g4,fp0,g4",
                        r"89a74:.*subrl.*fp0,g4,g4", r"89a78:.*mov.*10,r13",
                        r"89a7c:.*ld.*0x51c948", r"89a84:.*st.*r13,0x884000",
                        r"89a94:.*st.*g6,0x884000", r"89a9c:.*st.*g4,0x884000",
                        r"89aa4:.*ld.*0x884000", r"89ab0:.*st.*g7,0x51c94c",
                        r"89ab8:.*cmpi.*g4,0", r"89abc:.*stos.*g5,0x51c944",
                        r"89ac4:.*bne.*0x89ad8"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_899d8_float_tail
        function.argtypes = [ctypes.c_uint32] * 7
        function.restype = Result

        negative = function(0xbf800000, 0x3f000000, 0x11223344, 0x42a00000, 0x55, 0, 0xdeadbeef)
        assert (negative.selected_float, negative.computed_command_word) == (0xbf800000, 0xbfc00000)
        assert (negative.state_51c940, negative.state_51c944, negative.state_51c94c,
                negative.state_51c9b4, negative.continuation) == (
                    0x11223344, 0x55, 0xbf800000, 1, 0x89ac8)

        positive = function(0x3f800000, 0x3f000000, 0x11223344, 0x42a00000, 0x66, 7, 0xdeadbeef)
        assert (positive.selected_float, positive.computed_command_word,
                positive.packet_10_0, positive.packet_10_1, positive.packet_10_2) == (
                    0x41f00000, 0x41ec0000, 10, 0x42a00000, 0x41ec0000)
        assert (positive.state_51c940, positive.state_51c944, positive.state_51c94c,
                positive.state_51c9b4, positive.helper_call, positive.fifo_address,
                positive.command, positive.continuation) == (
                    0x11223344, 0x66, 0x41f00000, 0xdeadbeef,
                    0x6ece0, 0x884000, 10, 0x89ad8)
    print("recovered 0x899d8 floating-tail vectors: ok")


if __name__ == "__main__":
    main()
