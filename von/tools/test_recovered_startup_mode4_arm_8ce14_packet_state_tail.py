#!/usr/bin/env python3
"""Vectors for the 0x8ce14 gate-1 packet/state tail."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8ce14_packet_state_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32 * size) for name, size in (
        ("command_31_word", 6), ("command_29_word", 2),
        ("command_30_word", 2), ("command_10_word", 4))]
    _fields_ += [(name, ctypes.c_uint32) for name in (
        "response_51c948", "response_51c958", "response_51c960", "response_51c940",
        "response_51c944", "response_51c94c", "response_51c95c", "record_30")]
    _fields_ += [(name, ctypes.c_uint32 * size) for name, size in (
        ("command_31_packet", 7), ("command_29_packet", 3),
        ("command_30_packet", 3), ("command_10_packet_0", 3),
        ("command_10_packet_1", 3))]
    _fields_ += [(name, ctypes.c_uint32) for name in (
        "state_51c940", "state_51c944", "state_51c948", "state_51c958",
        "state_51c960", "state_51c94c", "state_51c95c", "fifo_address",
        "command_31", "command_29", "command_30", "command_10",
        "record_zero_path", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8ce14:.*mov.*0,r8", r"8ce18:.*ld.*0x5770f0,g4",
        r"8ce40:.*ld.*0x51c984,g4", r"8ce50:.*cvtir.*g4,r4",
        r"8ce58:.*mov.*31,r13", r"8ce7c:.*divrl.*r6,g0,g0",
        r"8ce8c:.*st.*g5,0x884000", r"8cea8:.*st.*g3,0x884000",
        r"8ceb0:.*st.*g7,0x884000", r"8cec0:.*ld.*0x884000,g4",
        r"8cecc:.*mulrl.*fp0,g0,g0", r"8ced0:.*ldos.*0x51c940,g4",
        r"8ced8:.*mov.*29,r12", r"8cef4:.*st.*g2,0x884000",
        r"8cf08:.*mov.*30,r13", r"8cf14:.*st.*g4,0x884000",
        r"8cf24:.*ld.*0x884000,g7", r"8cf84:.*st.*g1,0x51c958",
        r"8cfa4:.*st.*g4,0x51c94c", r"8cfc0:.*st.*g0,0x884000",
        r"8d000:.*mov.*10,r13", r"8d018:.*st.*g0,0x884000",
        r"8d028:.*ld.*0xc\(r10\),g4", r"8d050:.*st.*r12,0x884000",
        r"8d060:.*st.*g1,0x884000", r"8d068:.*st.*g6,0x884000",
        r"8d078:.*ldos.*0x30\(r10\),g4", r"8d07c:.*stos.*g0,0x51c940",
        r"8d084:.*cmpi.*g4,0", r"8d090:.*bne.*0x8d0a4"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8ce14_packet_state_tail
        u32_array = ctypes.c_uint32 * 6
        u32_pair = ctypes.c_uint32 * 2
        u32_quad = ctypes.c_uint32 * 4
        function.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                             ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)] + [ctypes.c_uint32] * 8
        function.restype = Result
        packet31 = u32_array(1, 2, 3, 4, 5, 6)
        packet29 = u32_pair(7, 8)
        packet30 = u32_pair(9, 10)
        packet10 = u32_quad(11, 12, 13, 14)
        zero = function(packet31, packet29, packet30, packet10, 15, 16, 17, 18, 19, 20, 21, 0)
        assert list(zero.command_31_packet) == [31, 1, 2, 3, 4, 5, 6]
        assert list(zero.command_29_packet) == [29, 7, 8]
        assert list(zero.command_30_packet) == [30, 9, 10]
        assert list(zero.command_10_packet_0) == [10, 11, 12]
        assert list(zero.command_10_packet_1) == [10, 13, 14]
        assert (zero.state_51c940, zero.state_51c944, zero.state_51c94c,
                zero.record_zero_path, zero.continuation) == (18, 19, 20, 1, 0x8d094)
        nonzero = function(packet31, packet29, packet30, packet10, 15, 16, 17, 18, 19, 20, 21, 1)
        assert (nonzero.record_zero_path, nonzero.continuation) == (0, 0x8d0a4)
    print("recovered 0x8ce14 packet/state-tail vectors: ok")


if __name__ == "__main__":
    main()
