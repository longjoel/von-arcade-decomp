#!/usr/bin/env python3
"""Vectors for the 0x8c840 selector-3 scale/packet tail."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8c840_scale_packet_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "selected_float", "record_0c", "response_51c948", "computed_state_51c94c",
        "command_10_word", "response_word", "record_30")]
    _fields_ += [("command_10_packet", ctypes.c_uint32 * 3)]
    _fields_ += [(name, ctypes.c_uint32) for name in (
        "state_51c94c", "state_51c944", "backup_51c964", "backup_51c968",
        "backup_51c96c", "backup_51c970", "backup_51c974", "backup_51c978",
        "command_10", "fifo_address", "record_zero_path", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8c840:.*ld.*0x5770f0,g4", r"8c848:.*cmpibne.*0,g4,0x8c868",
        r"8c854:.*lda.*0x40140000,g5", r"8c868:.*movr.*g0,fp0",
        r"8c870:.*lda.*0x40200000,g5", r"8c888:.*ld.*0xc\(r4\),g6",
        r"8c890:.*lda.*0x402e0000,g5", r"8c8a4:.*mov.*10,r9",
        r"8c8a8:.*ld.*0x51c948,g6", r"8c8b0:.*st.*r9,0x884000",
        r"8c8c0:.*st.*g6,0x884000", r"8c8c8:.*st.*g4,0x884000",
        r"8c8d8:.*ldos.*0x30\(r5\),g4", r"8c8dc:.*st.*g7,0x51c94c",
        r"8c8e8:.*stos.*g5,0x51c944", r"8c8f0:.*bne.*0x8c904",
        r"8c8f4:.*mov.*1,r8", r"8c904:.*st.*g14,0x51c9b4",
        r"8c90c:.*ld.*0x51c950,r9", r"8c964:.*st.*r8,0x51c978"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8c840_scale_packet_tail
        function.argtypes = [ctypes.c_uint32] * 12
        function.restype = Result
        zero = function(0x40800000, 0x12, 0x42a00000, 0x40a00000, 0x1234, 0x5678,
                       0, 0x11, 0x22, 0x33, 0x44, 0x55)
        assert list(zero.command_10_packet) == [10, 0x42a00000, 0x1234]
        assert (zero.state_51c94c, zero.state_51c944, zero.backup_51c964,
                zero.backup_51c968, zero.backup_51c96c, zero.backup_51c970,
                zero.backup_51c974, zero.backup_51c978,
                zero.record_zero_path, zero.continuation) == (0x40a00000, 0x5678,
                                                               0x11, 0x40a00000, 0x33,
                                                               0x22, 0x44, 0x55, 1, 0x8c8f4)
        nonzero = function(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
        assert (nonzero.record_zero_path, nonzero.continuation) == (0, 0x8c904)
    print("recovered 0x8c840 scale/packet-tail vectors: ok")


if __name__ == "__main__":
    main()
