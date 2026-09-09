#!/usr/bin/env python3
"""Verify the recovered 0x934b0 geometry FIFO command packet.

Packet shape decoded from vonj-maincpu.lst; caller arg goldens read
from the two sampled call sites (0x99afc, 0x96988). The 0x884000 FIFO
writes and the 0x8e310 tail call are MMIO/code effects outside the
contract; only the word sequence and call-arg formation are modeled.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_fifo_packet_934b0.c"

FIXED = [5, 18, None, None, None, 21, None, 19,
         0x3E4CCCCD, 0x3E4CCCCD, 0x3E4CCCCD, 6]

CALLERS = [
    # The eleven fixed-vector calls in the 0x99afc-0x99c5c ladder.
    (0x00000000, 0x4181999A, 0xC0666666, 0xFFFFC000, 0xC000),
    (0x40000000, 0x4181999A, 0xC0666666, 0xFFFFC000, 0xC000),
    (0x40800000, 0x4181999A, 0xC0666666, 0xFFFFC000, 0xC000),
    (0x40C00000, 0x4181999A, 0xC0666666, 0xFFFFC000, 0xC000),
    (0x41000000, 0x4181999A, 0xC0666666, 0xFFFFC000, 0xC000),
    (0x41200000, 0x4181999A, 0xC0666666, 0xFFFFC000, 0xC000),
    (0xC0000000, 0x4181999A, 0xC0666666, 0xFFFFC000, 0xC000),
    (0xC0800000, 0x4181999A, 0xC0666666, 0xFFFFC000, 0xC000),
    (0xC0C00000, 0x4181999A, 0xC0666666, 0xFFFFC000, 0xC000),
    (0xC1000000, 0x4181999A, 0xC0666666, 0xFFFFC000, 0xC000),
    (0xC1200000, 0x4181999A, 0xC0666666, 0xFFFFC000, 0xC000),
    # The independent sampled caller at 0x96988.
    (0x40800000, 0x4240CCCD, 0x416CCCCD, 0xFFFFC000, 0xC000),
]


class TailArgs(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in "a0 a1 a2".split()]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-fifo-pkt-") as directory:
        library = Path(directory) / "fifo-pkt.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
             str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        lib.fifo_packet_build.argtypes = [ctypes.c_uint32] * 4 + [
            ctypes.POINTER(ctypes.c_uint32)]
        lib.fifo_packet_build.restype = None
        lib.fifo_packet_tail_args.argtypes = [ctypes.c_uint32,
                                              ctypes.POINTER(TailArgs)]
        lib.fifo_packet_tail_args.restype = None

        for g0, g1, g2, g3, w6 in CALLERS:
            words = (ctypes.c_uint32 * 12)()
            lib.fifo_packet_build(g0, g1, g2, g3, words)
            expected = list(FIXED)
            expected[2:5] = [g0, g1, g2]
            expected[6] = w6
            assert list(words) == expected, hex(g0)
            assert words[6] == g3 & 0xFFFF, "g3 mask"

        out = TailArgs()
        lib.fifo_packet_tail_args(0x12345678, ctypes.byref(out))
        assert out.a0 == 0x02B68D3A, hex(out.a0)
        assert out.a1 == (0x02B68D3A + 0x79E2A) & 0xFFFFFFFF, hex(out.a1)
        assert out.a2 == 0x12345678, "mem passthrough"
        print("PASS: 12-word packet x12 callers, tail args")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
