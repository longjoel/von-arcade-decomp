#!/usr/bin/env python3
"""Verify the 0x93240 float-prologue FIFO packet.

Pins the prologue index/cell rule on both legs, the float32 w2 sum,
the standard 12-word template against two observed caller arg sets,
and the tail-call formation (a1 cross-checked by open-coded integer
arithmetic, not the model). Live FIFO/MMIO transports and the 0x8e310
tail call stay outside the contract.
"""

from __future__ import annotations

import ctypes
import os
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_fifo_prologue_93240.c"

F = 0x3E4CCCCD
NEG30 = 0xC1F00000


def fbits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


class TailArgs(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in "a0 a1 a2".split()]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-fifo-pro-") as directory:
        library = Path(directory) / "fifo-pro.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
             str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        lib.prologue_init.argtypes = [ctypes.c_uint32]
        lib.prologue_init.restype = ctypes.c_uint32
        lib.prologue_cell.argtypes = [ctypes.c_uint32]
        lib.prologue_cell.restype = ctypes.c_uint32
        lib.fadd_bits.argtypes = [ctypes.c_uint32] * 2
        lib.fadd_bits.restype = ctypes.c_uint32
        lib.fifo_prologue_packet_build.argtypes = [ctypes.c_uint32] * 4 + [
            ctypes.POINTER(ctypes.c_uint32)]
        lib.fifo_prologue_packet_build.restype = None
        lib.fifo_prologue_tail_args.argtypes = [ctypes.c_uint32,
                                                ctypes.POINTER(TailArgs)]
        lib.fifo_prologue_tail_args.restype = None

        assert lib.prologue_init(0) == 0xBFFF, "init"
        assert lib.prologue_init(0x4001) == 0, "wrap"
        assert lib.prologue_init(0x5000) == 0xFFF, "low leg"

        assert lib.prologue_cell(0xBFFF) == NEG30, "high leg"
        assert lib.prologue_cell(0x7FFF) == NEG30, "high edge"
        assert lib.prologue_cell(0x7FFE) == 0x7FFE, "low edge keeps"
        assert lib.prologue_cell(0xFFF) == 0xFFF, "low leg keeps"
        assert lib.prologue_cell(0) == 0, "zero keeps (nearest-even)"

        assert lib.fadd_bits(0, NEG30) == NEG30, "0 + -30"
        assert lib.fadd_bits(fbits(1.0), 10) == fbits(1.0), "absorbs"

        for g0, g1, g2 in ((0x00000000, 0x41B40000, 0xC195999A),
                           (0x00000000, 0x41B4CCCD, 0xC19A6666)):
            cell = lib.prologue_cell(lib.prologue_init(0))
            assert cell == NEG30
            words = (ctypes.c_uint32 * 12)()
            lib.fifo_prologue_packet_build(
                lib.fadd_bits(g0, cell), g1, g2, 0, words)
            assert list(words) == [
                5, 18, NEG30, g1, g2, 21, 0, 19, F, F, F, 6], hex(g1)

        out = TailArgs()
        lib.fifo_prologue_tail_args(77, ctypes.byref(out))
        assert out.a0 == 0x02B4B652, hex(out.a0)
        assert out.a1 == (0x02B4B652 + 0x97512) & 0xFFFFFFFF, hex(out.a1)
        assert out.a2 == 77 % 30, "unsigned remainder"
        print("PASS: prologue legs, fadd, packet x2, tail args")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
