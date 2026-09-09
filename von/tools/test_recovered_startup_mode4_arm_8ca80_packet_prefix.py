#!/usr/bin/env python3
"""Validate the common command-10/29/30 prefix of the 0x8ca80 arms."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_8ca80_packet_prefix.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "entry", "endpoint_a0", "endpoint_a1", "endpoint_b0", "endpoint_b1",
        "delta_a", "delta_b", "fifo_response", "masked_lane",
        "packet10_0", "packet10_1", "packet10_2", "packet29_0", "packet29_1",
        "packet29_2", "packet30_0", "packet30_1", "packet30_2", "fifo_address",
        "command29_constant", "command30_constant", "continuation")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "packet.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8ca80_packet_prefix
        fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        for entry, continuation in ((0x8cac8, 0x8cb00), (0x8ccfc, 0x8cd30)):
            result = Result()
            assert fn(entry, 0x100, 0x80, 0x240, 0x200, 0x12345678,
                      ctypes.byref(result)) == 1
            assert (result.entry, result.continuation) == (entry, continuation)
            assert (result.delta_a, result.delta_b) == (0x140, 0x180)
            assert result.masked_lane == 0x8678
            assert (result.packet10_0, result.packet10_1, result.packet10_2) == (10, 0x180, 0x140)
            assert (result.packet29_0, result.packet29_1, result.packet29_2) == (29, 0x8678, 0x42200000)
            assert (result.packet30_0, result.packet30_1, result.packet30_2) == (30, 0x8678, 0x42200000)
            assert result.fifo_address == 0x884000
    print("PASS: 0x8ca80 command packet prefix")


if __name__ == "__main__":
    main()
