#!/usr/bin/env python3
"""Verify the recovered 0x76030 post-call setup tail.

Goldens from spawn dumps d1/d2/d4 (post-call g14 = 0, r4 = -1):
consts e1c = 1, e48 = 6, e20/e24 = -1, rest 0.
0x72400 rows read live from ROM: S3 (both attempts) = row 2,
S4 = row 3.
0x72370 entries read live from ROM: S3 attempt 1 = entry 4
(e34 4f / e38 55615b / e3c 3c003c / e40 3c), S3 attempt 3 =
entry 6, S4 = entry 3.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_stage_postcall_76030.c"

ROW2 = [0x0064FF24, 0xFEFC001E, 0x001E003C, 0x003CFF24, 0xFFB0001E,
        0x003C00F0, 0x00000000, 0x00F00000, 0x003C0050, 0x00000000,
        0x00000000, 0x00000000]
ROW3 = [0x00000000] * 12


class Consts(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in
                "e1c e42 e44 e20 e24 e28 e2c e50 e4c e48 "
                "b8c b90 b94 b98".split()]


class Entry(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in "e34 e38 e3c e40".split()]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-stage-postcall-") as directory:
        library = Path(directory) / "stage-postcall.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
             str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        lib.row724_address.argtypes = [ctypes.c_uint32]
        lib.row724_address.restype = ctypes.c_uint32
        lib.row724_lookup.argtypes = [ctypes.c_uint32]
        lib.row724_lookup.restype = ctypes.POINTER(ctypes.c_uint32)
        lib.row724_tail_half.argtypes = [ctypes.c_uint32]
        lib.row724_tail_half.restype = ctypes.c_uint32
        lib.row724_copy.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32)]
        lib.row724_copy.restype = None
        lib.read370.argtypes = [ctypes.c_uint,
                                ctypes.POINTER(Entry)]
        lib.read370.restype = None
        lib.second370_key.argtypes = [ctypes.c_uint32] * 3
        lib.second370_key.restype = ctypes.c_uint32
        lib.postcall_consts.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32,
            ctypes.POINTER(Consts)]
        lib.postcall_consts.restype = None

        for idx in range(8):
            assert lib.row724_address(idx) == 0x72400 + idx * 50, idx
        assert not lib.row724_lookup(8), "oob row"
        assert (lib.row724_tail_half(2),
                lib.row724_tail_half(3)) == (0x190, 0x226), "halves"

        for idx, expected, half in ((2, ROW2, 0x190), (3, ROW3, 0x226)):
            dst = (ctypes.c_uint32 * 12)()
            out_half = ctypes.c_uint32(0)
            lib.row724_copy(lib.row724_lookup(idx),
                            lib.row724_tail_half(idx),
                            dst, ctypes.byref(out_half))
            assert list(dst) == expected, f"row724 {idx}"
            assert out_half.value == half, f"row724 {idx} half"

        for key, e34, e38, e3c, e40 in (
                (4, 0x4F, 0x55615B, 0x3C003C, 0x3C),
                (6, 0x97, 0x91008B, 0x3C003C, 0x3C),
                (3, 0x49, 0x43003D, 0x0064005A, 0x3C)):
            out = Entry()
            lib.read370(key, ctypes.byref(out))
            assert (out.e34, out.e38, out.e3c,
                    out.e40) == (e34, e38, e3c, e40), f"entry {key}"

        assert lib.second370_key(0, 9, 12) == 4, "a9c branch"
        assert lib.second370_key(7, 9, 12) == 1, "a98 branch"

        out = Consts()
        lib.postcall_consts(0, 0xFFFFFFFF, ctypes.byref(out))
        assert (out.e1c, out.e48) == (1, 6), "consts"
        assert (out.e20, out.e24) == (0xFFFFFFFF, 0xFFFFFFFF), "r4"
        for name in ("e42", "e44", "e28", "e2c", "e50", "e4c",
                     "b8c", "b90", "b94", "b98"):
            assert getattr(out, name) == 0, name
        print("PASS: post-call consts, 724 rows 2/3, 370 entries 3/4/6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
