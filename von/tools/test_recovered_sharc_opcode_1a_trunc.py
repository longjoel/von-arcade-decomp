#!/usr/bin/env python3
"""Verify the truncating SHARC opcode-0x1a affine model and the live
07-load/1a compose privileging neither engine.

Live forced-FIFO compose (harness spec "10;07:<12 words>;1a:<3
words>;fd:3" on a discriminating matrix) drains 42e09999/4354eeee
under DRC but 42e0999a/4354eeef under the interpreter; the third
column agrees (43b67333). This test pins the truncating
(hardware/DRC) words. The existing
von/tools/test_recovered_sharc_opcode_1a.py pins the interpreter
rounding instead and is labeled as such.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_1a_trunc.c"

STATE = [
    0x3DCCCCCD, 0x3E4CCCCD, 0x3E99999A,
    0x3FD9999A, 0x40000000, 0x40400000,
    0x3F000000, 0x3EAAAAAB, 0x40E00000,
    0x42C80000, 0x43480000, 0x43960000,
]
VECTOR = [0x40400000, 0x40A00000, 0x40E00000]
# Live DRC drain words for the STATE/VECTOR compose above.
EXPECTED_TRUNC = (0x42E09999, 0x4354EEEE, 0x43B67333)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-1a-trunc-") as directory:
        library = Path(directory) / "op1a_trunc.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-std=c99", "-O2", "-shared",
             "-fPIC", str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        affine = lib.sharc_opcode_1a_affine_trunc
        affine.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                           ctypes.POINTER(ctypes.c_uint32),
                           ctypes.POINTER(ctypes.c_uint32)]
        affine.restype = None
        vec = (ctypes.c_uint32 * 3)(*VECTOR)
        out = (ctypes.c_uint32 * 3)()
        state = (ctypes.c_uint32 * 12)(*STATE)
        affine(vec, state, out)
        assert tuple(out) == EXPECTED_TRUNC, [hex(v) for v in out]

        # Identity compose stays exact under both roundings.
        # True layout (matches the C header and the live golden above):
        # column j = words j, 3+j, 6+j; translation = words 9..11.
        ident = (ctypes.c_uint32 * 12)(
            0x3F800000, 0, 0,
            0, 0x3F800000, 0,
            0, 0, 0x3F800000,
            0x41A00000, 0x41A80000, 0x41F80000)
        vec2 = (ctypes.c_uint32 * 3)(0x3F800000, 0x40000000, 0x40400000)
        affine(vec2, ident, out)
        assert tuple(out) == (0x41A80000, 0x41B80000, 0x42080000), \
            [hex(v) for v in out]

        # Huge-gap subtract drops exactly one ulp toward zero, even
        # when the subtrahend is a fraction of an ulp (gap >= 63).
        # Column 0 chains two: gap 67 (one-ulp borrow at 1.0 -> exp-1)
        # then gap 62 through the general path. Columns 1 and 2 pin
        # the no-borrow and negative sides. The old gap>=64 shortcut
        # returned (0x3F800000, 0x40400000, 0xBF800000) here.
        import struct as _st
        neg_tiny = _st.unpack('<I', _st.pack('<f', -1e-20))[0]
        pos_tiny = _st.unpack('<I', _st.pack('<f', 1e-20))[0]
        neg_pow = _st.unpack('<I', _st.pack('<f', -(2.0 ** -63)))[0]
        assert (neg_tiny, pos_tiny, neg_pow) == \
            (0x9E3CE508, 0x1E3CE508, 0xA0000000)
        vec3 = (ctypes.c_uint32 * 3)(0x3F800000, 0x3F800000, 0x3F800000)
        gap_state = (ctypes.c_uint32 * 12)(
            neg_tiny, neg_tiny, pos_tiny,
            neg_pow, 0, 0,
            0, 0, 0,
            0x3F800000, 0x40400000, 0xBF800000)
        affine(vec3, gap_state, out)
        assert tuple(out) == (0x3F7FFFFE, 0x403FFFFF, 0xBF7FFFFF), \
            [hex(v) for v in out]
        print("PASS: SHARC 1a affine truncating compose "
              "(live DRC drain goldens)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
