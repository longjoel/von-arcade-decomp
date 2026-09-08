#!/usr/bin/env python3
"""Verify the 0x90c10/0x90d50/0x90e80 table-dispatched FIFO template.

One shared template, three site constants. The test pins the 14-word
packet, the mod-30 index, spot entries of the live-read ROM table
(von/build/probe_dispatch_table.lua), and the register-block skip /
write rule. Live MMIO transports stay outside the contract.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_fifo_dispatch_90c10.c"

SITES = (0xB800, 0xC000, 0xC800)


class Regs(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in
                "do_write w800010 w804000 w804004 w804008 w80400c".split()]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-fifo-disp-") as directory:
        library = Path(directory) / "fifo-disp.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
             str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        lib.fifo_dispatch_packet_build.argtypes = [ctypes.c_uint32] * 3 + [
            ctypes.POINTER(ctypes.c_uint32)]
        lib.fifo_dispatch_packet_build.restype = None
        lib.fifo_dispatch_index.argtypes = [ctypes.c_uint32]
        lib.fifo_dispatch_index.restype = ctypes.c_uint32
        lib.fifo_dispatch_lookup.argtypes = [ctypes.c_uint32]
        lib.fifo_dispatch_lookup.restype = ctypes.POINTER(ctypes.c_uint32)
        lib.fifo_dispatch_regs.argtypes = [ctypes.c_uint32] * 3 + [
            ctypes.POINTER(Regs)]
        lib.fifo_dispatch_regs.restype = None

        for site in SITES:
            words = (ctypes.c_uint32 * 14)()
            lib.fifo_dispatch_packet_build(7, site, 0xDEAD, words)
            assert list(words) == [
                5, 18, 0x40E00000, 0x41800000, 7, 21, site, 19,
                0x40400000, 0x40400000, 0x40400000, 58, 0xDEAD, 6], hex(site)

        for g0, idx in ((0, 0), (29, 29), (30, 0), (31, 1), (59, 29)):
            assert lib.fifo_dispatch_index(g0) == idx, g0

        assert not lib.fifo_dispatch_lookup(30), "oob"
        for idx, expected in (
                (0, [0, 0, 0]),
                (1, [0x00400C54, 0x00400C54, 0x0084695E]),
                (29, [0x00400CC4, 0x00400CC4, 0x0084C94A])):
            assert list(lib.fifo_dispatch_lookup(idx)[:3]) == expected, idx

        out = Regs()
        lib.fifo_dispatch_regs(0, 1, 2, ctypes.byref(out))
        assert out.do_write == 0, "null skips"
        lib.fifo_dispatch_regs(0x99, 0x00400C54, 0x0084695E,
                               ctypes.byref(out))
        assert (out.do_write, out.w800010, out.w804000, out.w804004,
                out.w804008, out.w80400c) == (
                    1, 0x101, 0x99, 0x00400C54, 0x0084695E, 0), "writes"
        print("PASS: packet x3 sites, index, table spots, regs rule")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
