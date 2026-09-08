#!/usr/bin/env python3
"""Verify the recovered 0x92830 FIFO packet site.

The 12-word packet template is shared with 0x934b0 (covered by its own
test); this test pins the 0x92830 site constants: tail-call base
0x02b4a4bc with offset 0x98750, and the [0x562494] call-arg word. The
live FIFO writes and the 0x8e310 tail call stay outside the contract.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_fifo_packet_92830.c"


class TailArgs(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in "a0 a1 a2".split()]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-fifo-92830-") as directory:
        library = Path(directory) / "fifo-92830.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
             f"-I{ROOT}", str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        lib.fifo_packet_92830_tail_args.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(TailArgs)]
        lib.fifo_packet_92830_tail_args.restype = None
        lib.fifo_packet_build.argtypes = [ctypes.c_uint32] * 4 + [
            ctypes.POINTER(ctypes.c_uint32)]
        lib.fifo_packet_build.restype = None

        out = TailArgs()
        lib.fifo_packet_92830_tail_args(0xA5A5A5A5, ctypes.byref(out))
        assert out.a0 == 0x02B4A4BC, hex(out.a0)
        assert out.a1 == (0x02B4A4BC + 0x98750) & 0xFFFFFFFF, hex(out.a1)
        assert out.a2 == 0xA5A5A5A5, "mem passthrough"

        words = (ctypes.c_uint32 * 12)()
        lib.fifo_packet_build(1, 2, 3, 4, words)
        assert (words[0], words[1], words[5], words[7],
                words[11]) == (5, 18, 21, 19, 6), "shared template"
        assert (words[2], words[3], words[4],
                words[6]) == (1, 2, 3, 4), "payload passthrough"
        print("PASS: 0x92830 site constants, shared packet template")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
