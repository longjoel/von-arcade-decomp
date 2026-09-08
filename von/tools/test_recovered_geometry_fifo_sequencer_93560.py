#!/usr/bin/env python3
"""Verify the 0x93560 geometry FIFO sequencer.

Pins the 12-word prefix packet, the C8 gated store, the modulo-120
selector path, and every leg of the modulo-168 sequencer including
the 59/23/59 boundary edges. Live FIFO/MMIO transports, the 0xf5058
subroutine (its g0 arrives as an input), and the 0x8e310 tail call
stay outside the contract.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_fifo_sequencer_93560.c"

F = 0x3E4CCCCD


class Step(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in
                "wrote_c8 c8_new cc_new a0 a1 a2".split()]


def check(lib, post_bal, c8, cc, exp):
    out = Step()
    lib.fifo_seq_step(post_bal, c8, cc, ctypes.byref(out))
    got = (out.wrote_c8, out.c8_new, out.cc_new,
           out.a0, out.a1, out.a2)
    assert got == exp, f"bal={post_bal} c8={c8} cc={cc}: {got} != {exp}"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-fifo-seq-") as directory:
        library = Path(directory) / "fifo-seq.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
             str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        lib.fifo_seq_packet_build.argtypes = [ctypes.c_uint32] * 4 + [
            ctypes.POINTER(ctypes.c_uint32)]
        lib.fifo_seq_packet_build.restype = None
        lib.fifo_seq_step.argtypes = [ctypes.c_uint32] * 3 + [
            ctypes.POINTER(Step)]
        lib.fifo_seq_step.restype = None

        words = (ctypes.c_uint32 * 12)()
        lib.fifo_seq_packet_build(1, 2, 3, 0x1FFFF, words)
        assert list(words) == [
            5, 18, 1, 2, 3, 21, 0xFFFF, 19, F, F, F, 6], "packet"

        B1, B2, BS, A1 = 0x02B5C3A6, 0x02B60728, 0x02B58024, 0x02BE2B64
        check(lib, 99, 7, 10,
              (0, 7, 11, BS, A1, 11))
        check(lib, 5, 0, 0,
              (1, 1, 1, B1, A1, 1))
        check(lib, 6, 0, 0,
              (1, 2, 1, B2, A1, 1))
        check(lib, 7, 9, 0,
              (1, 3, 1, BS, A1, 1))
        check(lib, 99, 1, 119,
              (0, 1, 0, B1, A1, 0))
        check(lib, 99, 0, 59,
              (0, 0, 60, BS, A1, 60))
        check(lib, 99, 3, 82,
              (0, 3, 83, BS, A1, 0x77))
        check(lib, 99, 3, 143,
              (0, 3, 144, BS, A1, 0x77))
        check(lib, 99, 3, 142,
              (0, 3, 143, BS, A1, 119))
        check(lib, 99, 0, 100,
              (0, 0, 101, BS, A1, 77))
        print("PASS: packet, gated store, mod-120, sequencer edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
