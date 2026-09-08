#!/usr/bin/env python3
"""Verify the SHARC opcode-0x05 window slide and 0x06 rewind models.

Live forced-FIFO marker probes pin the data move: words 1..12 staged
at DM 0x30200 appear verbatim at 0x3020c..0x30217 with 0x30218+
untouched, which admits only the M7-displacement walk (a premodify
walk would scatter to P+12,P+24,... while reading back its own
writes). The counter+1/pointer+12 saves and the saturating guards are
listing work (0x16d-0x172, 0x18d-0x198): the attract-mode 08 stream
resets both within frames of any trial, so no post-trial snapshot can
catch them. ROM-free: all goldens are hardcoded captures, no MAME.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_stack_05_06.c"

# Live post-05 snapshot words (two boots agree).
LIVE_SRC = list(range(1, 13))
LIVE_DST = list(range(1, 13))
LIVE_TAIL = [0x21, 0x22, 0x23, 0x24, 0x25, 0x26,
             0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C]


class PushOut(ctypes.Structure):
    _fields_ = [("depth", ctypes.c_uint32), ("ptr", ctypes.c_uint32)]


class PopOut(ctypes.Structure):
    _fields_ = [("depth", ctypes.c_uint32), ("ptr", ctypes.c_uint32)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-slide-") as directory:
        library = Path(directory) / "slide.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-std=c99", "-O2", "-shared",
             "-fPIC", str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        push = lib.sharc_stack_push_copy
        push.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(ctypes.c_uint32),
                         ctypes.POINTER(PushOut)]
        push.restype = None
        pop = lib.sharc_stack_pop
        pop.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(PopOut)]
        pop.restype = None

        window = (ctypes.c_uint32 * 24)(*LIVE_SRC, *LIVE_TAIL)
        out = PushOut()
        push(0, 0x30200, window, out)
        assert (out.depth, out.ptr) == (1, 0x3020C), (out.depth, hex(out.ptr))
        assert list(window[:12]) == LIVE_SRC
        assert list(window[12:24]) == LIVE_DST, [hex(v) for v in window[12:24]]

        # Saturation: depth 7 is a full no-op (IF GE, RTS).
        frozen = (ctypes.c_uint32 * 24)(*[0xAA] * 24)
        push(7, 0x30200, frozen, out)
        assert (out.depth, out.ptr) == (7, 0x30200)
        assert list(frozen) == [0xAA] * 24

        # Rewind: nonzero decrements and pulls the pointer back 12;
        # depth 0 is a no-op (IF EQ, RTS) with no data move by design.
        popout = PopOut()
        pop(1, 0x3020C, popout)
        assert (popout.depth, popout.ptr) == (0, 0x30200)
        pop(0, 0x30200, popout)
        assert (popout.depth, popout.ptr) == (0, 0x30200)
        print("PASS: SHARC 05 window slide and 06 rewind "
              "(live slide goldens)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
