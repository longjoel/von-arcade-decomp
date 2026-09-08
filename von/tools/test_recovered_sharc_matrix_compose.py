#!/usr/bin/env python3
"""Verify the SHARC 07->09->1a->11 matrix compose end to end.

Chains the recovered C models (07 verbatim store, 09 consecutive-triplet
transform, 1a truncating affine, 11 readback) and pins the live
forced-FIFO drains captured under default DRC:

- identity matrix: 09 reproduces its inputs, 1a drains
  43fcd110/44b0a333/439ccccc, 11 streams the input block back;
- cyclic-shift matrix out=(y,z,x): 09 shifts each triplet in place, 1a
  drains 44b0a333/439ccccc/43fcd110, 11 streams the derived block back.

The -nodrc interpreter agrees on the 09/11 stages (exact 0/1 regime) and
rounds the 1a drains up one ulp where they differ (documented pair, not
asserted here). ROM-free: all goldens are hardcoded captures, no MAME.
"""

from __future__ import annotations

import ctypes
import os
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ROOT / "von/i960/recovered_sharc_opcode_07_store.c",
    ROOT / "von/i960/recovered_sharc_opcode_09.c",
    ROOT / "von/i960/recovered_sharc_opcode_1a_trunc.c",
    ROOT / "von/i960/recovered_sharc_state_08_0e_10_11_19.c",
]

I = 0x3F800000
IDENTITY_M = [I, 0, 0, 0, I, 0, 0, 0, I, 0, 0, 0]
SHIFT_M = [0, 0, I, I, 0, 0, 0, I, 0, 0, 0, 0]
V = [0x3DCCCCCD, 0x3FD9999A, 0x3F000000, 0x42C80000,
     0x3E4CCCCD, 0x40000000, 0x3EAAAAAB, 0x43480000,
     0x3E99999A, 0x40400000, 0x40E00000, 0x43960000]
X = [0x40400000, 0x40A00000, 0x40E00000]

# Live DRC goldens: (1a drain triple, 11 readback block).
IDENTITY_GOLDEN = (
    (0x43FCD110, 0x44B0A333, 0x439CCCCC),
    tuple(V),
)
SHIFT_GOLDEN = (
    (0x44B0A333, 0x439CCCCC, 0x43FCD110),
    (0x3FD9999A, 0x3F000000, 0x3DCCCCCD,
     0x3E4CCCCD, 0x40000000, 0x42C80000,
     0x43480000, 0x3E99999A, 0x3EAAAAAB,
     0x40E00000, 0x43960000, 0x40400000),
)


def words_to_floats(words):
    return [struct.unpack('<f', struct.pack('<I', w))[0] for w in words]


def floats_to_words(floats):
    return [struct.unpack('<I', struct.pack('<f', v))[0] for v in floats]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-compose-") as directory:
        library = Path(directory) / "compose.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-std=c99", "-O2", "-shared",
             "-fPIC", *[str(s) for s in SOURCES], "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        store07 = lib.recovered_sharc_opcode_07_store
        store07.argtypes = [ctypes.POINTER(ctypes.c_uint32)] * 2
        store07.restype = None
        transform09 = lib.recovered_sharc_opcode_09_transform
        transform09.argtypes = [ctypes.POINTER(ctypes.c_float)] * 3
        transform09.restype = None
        affine1a = lib.sharc_opcode_1a_affine_trunc
        affine1a.argtypes = [ctypes.POINTER(ctypes.c_uint32)] * 3
        affine1a.restype = None
        readback11 = lib.sharc_state_readback_11
        readback11.argtypes = [ctypes.POINTER(ctypes.c_uint32)] * 2
        readback11.restype = None

        words12 = ctypes.c_uint32 * 12
        words3 = ctypes.c_uint32 * 3
        floats12 = ctypes.c_float * 12
        floats9 = ctypes.c_float * 9

        for name, matrix, (want_drain, want_block) in (
                ("identity", IDENTITY_M, IDENTITY_GOLDEN),
                ("shift", SHIFT_M, SHIFT_GOLDEN)):
            record = words12()
            store07(words12(*matrix), record)
            assert list(record) == matrix, name

            derived = floats12()
            transform09(floats12(*words_to_floats(V)),
                        floats9(*words_to_floats(matrix[:9])), derived)
            assert tuple(floats_to_words(derived)) == want_block, name

            out = words3()
            affine1a(words3(*X), words12(*floats_to_words(derived)), out)
            assert tuple(out) == want_drain, \
                (name, [hex(v) for v in out])

            # 11 streams exactly the 12 derived words (no thirteenth;
            # live drains past twelve read empty-FIFO zero).
            stream = words12()
            readback11(words12(*floats_to_words(derived)), stream)
            assert tuple(stream) == want_block, name
        print("PASS: SHARC 07->09->1a->11 matrix compose "
              "(live DRC goldens)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
