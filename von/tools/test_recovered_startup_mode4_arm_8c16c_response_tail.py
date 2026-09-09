#!/usr/bin/env python3
"""Vectors for the 0x8c16c selector-0 response tail."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8c16c_response_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "adjusted_operand", "helper_result", "selected_float", "adjusted_float",
        "timing_5770f0", "first_command_10_word_1", "first_command_10_word_2",
        "second_command_10_word_1", "second_command_10_word_2", "first_response",
        "second_response", "state_51c948", "record_30")]
    _fields_ += [(name, ctypes.c_uint32 * 3) for name in (
        "command_10_packet_0", "command_10_packet_1")]
    _fields_ += [(name, ctypes.c_uint32) for name in (
        "state_51c940", "state_51c944", "state_51c94c", "fifo_address",
        "command", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8c16c:.*subo.*3,g4,g4", r"8c170:.*cmpo.*1,g4",
        r"8c184:.*bl.*0x8c1b8", r"8c190:.*call.*0x6ece0",
        r"8c1a8:.*ble.*0x8c1bc", r"8c1d0:.*lda.*0x40140000,g5",
        r"8c224:.*mov.*10,r9", r"8c238:.*st.*g6,0x884000",
        r"8c240:.*st.*g5,0x884000", r"8c270:.*mov.*10,r8",
        r"8c28c:.*st.*g6,0x884000", r"8c294:.*st.*g4,0x884000",
        r"8c2a8:.*stos.*g7,0x51c940", r"8c2b0:.*st.*g0,0x51c94c",
        r"8c2bc:.*stos.*g5,0x51c944", r"8c2c4:.*be.*0x8c904",
        r"8c2c8:.*b.*0x8c8f4"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8c16c_response_tail
        function.argtypes = [ctypes.c_uint32] * 13
        function.restype = Result
        zero = function(1, 2, 3, 4, 0, 5, 6, 7, 8, 9, 10, 11, 0)
        assert list(zero.command_10_packet_0) == [10, 5, 6]
        assert list(zero.command_10_packet_1) == [10, 7, 8]
        assert (zero.state_51c940, zero.state_51c944, zero.state_51c94c,
                zero.continuation) == (9, 10, 8, 0x8c904)
        nonzero = function(0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1)
        assert nonzero.continuation == 0x8c8f4
    print("recovered 0x8c16c response-tail vectors: ok")


if __name__ == "__main__":
    main()
