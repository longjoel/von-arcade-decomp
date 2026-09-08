#!/usr/bin/env python3
"""Verify the stateful 0x92730/0x933b0 FIFO packet template.

Both routines share one logic template (RAM cells differ only); the
test pins the 13-word packet against two observed caller arg sets, the
1-bit toggle truth table, and the tail-call arg formation. The live
0x884000 FIFO writes, the 0xf5058 subroutine, and the 0x8e310 tail
call stay outside the contract.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_fifo_packet_stateful_92730.c"

CALLERS = [
    (0xC12CCCCD, 0x4227999A, 0x3F800000, 0x1500, 0x1500),
    (0xC1066666, 0x42293333, 0x3FE66666, 0xFFFFA000, 0xA000),
]


class CallArgs(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in "a0 a1 a2".split()]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-fifo-st-") as directory:
        library = Path(directory) / "fifo-st.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
             str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        lib.fifo_packet_stateful_build.argtypes = [ctypes.c_uint32] * 5 + [
            ctypes.POINTER(ctypes.c_uint32)]
        lib.fifo_packet_stateful_build.restype = None
        lib.fifo_packet_stateful_toggle.argtypes = [ctypes.c_uint32] * 3
        lib.fifo_packet_stateful_toggle.restype = ctypes.c_uint32
        lib.fifo_packet_stateful_call_args.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32,
            ctypes.POINTER(CallArgs)]
        lib.fifo_packet_stateful_call_args.restype = None

        for g0, g1, g2, g3, w6 in CALLERS:
            words = (ctypes.c_uint32 * 13)()
            lib.fifo_packet_stateful_build(g0, g1, g2, g3, 7, words)
            assert (list(words[:6]) ==
                    [5, 44, g0, g1, g2, 7]), hex(g0)
            assert (list(words[6:]) ==
                    [w6, 7, 19, 0x3E4CCCCD, 0x3E4CCCCD,
                     0x3E4CCCCD, 6]), hex(g0)

        toggle = lib.fifo_packet_stateful_toggle
        assert toggle(9, 1, 0) == 0, "A nonzero: F kept"
        assert toggle(9, 1, 1) == 1, "A nonzero: F kept"
        assert toggle(0, 0x10, 0) == 0, "bit0 clear: F kept"
        assert toggle(0, 0x11, 0) == 1, "0->1"
        assert toggle(0, 0x11, 1) == 0, "1->0"

        args = CallArgs()
        lib.fifo_packet_stateful_call_args(0, 0x44, ctypes.byref(args))
        assert (args.a0, args.a1, args.a2) == (
            0x02B53CA2, 0x02BE2B64, 0x44), "F zero"
        lib.fifo_packet_stateful_call_args(1, 0x44, ctypes.byref(args))
        assert args.a0 == (0x02B53CA2 + 0xFFFFBC7E) & 0xFFFFFFFF, "F set"
        assert (args.a1, args.a2) == (0x02BE2B64, 0x44), "a1/a2"
        print("PASS: 13-word packet x2, toggle table, call args")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
