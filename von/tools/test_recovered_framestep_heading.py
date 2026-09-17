#!/usr/bin/env python3
"""Validate the recovered i960 frame-step heading integrator (0x37240-0x3734c).

Compiles von/i960/recovered_framestep_heading.c and replays every
(A=+0x186, B=+0x32, C=+0x34, E=+0x198) -> expected vector observed at the
frame-step write PCs (0x372b0 / 0x37350 / 0x37324) in the original capture.

The vectors are normalized in
von/tests/fixtures/framestep-heading/original-heading-vectors.json, produced by
von/tools/probe_framestep_fields.lua with -nodrc write taps.
"""

import ctypes
import json
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_framestep_heading.c"
FIXTURE = (ROOT / "von/tests/fixtures/framestep-heading/"
           "original-heading-vectors.json")

CC = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC"]

OBJ_SIZE = 0x300
BytePtr = ctypes.POINTER(ctypes.c_ubyte)

FIELDS = {"a_186": 0x186, "b_32": 0x32, "c_34": 0x34, "e_198": 0x198}


def set_u16(obj, offset, value):
    ctypes.cast(ctypes.byref(obj, offset),
                ctypes.POINTER(ctypes.c_uint16))[0] = value & 0xffff


def get_u16(obj, offset):
    return ctypes.cast(ctypes.byref(obj, offset),
                       ctypes.POINTER(ctypes.c_uint16))[0]


def main():
    fixture = json.loads(FIXTURE.read_text())
    vectors = fixture["vectors"]
    assert fixture["counts"] == {"0x32": 541, "0x34": 541, "0x198": 19}
    assert len(vectors) == 1101

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "framestep-heading.so"
        subprocess.run(CC + [str(SOURCE), "-o", str(library)], check=True)
        run = ctypes.CDLL(str(library)).recovered_framestep_heading_run
        run.argtypes = [BytePtr]
        run.restype = None

        obj = (ctypes.c_ubyte * OBJ_SIZE)()
        obj_ptr = ctypes.cast(obj, BytePtr)
        checked = 0

        for vector in vectors:
            for key, offset in FIELDS.items():
                set_u16(obj, offset, vector[key])
            # Sentinel so an unexpected +0x198 write is visible.
            set_u16(obj, 0x198, vector["e_198"])
            run(obj_ptr)
            field = vector["field"]
            offset = int(field, 16)
            actual = get_u16(obj, offset)
            assert actual == vector["expected"], (
                field, vector, hex(actual))
            checked += 1

        # The +0x198 latch is written only on the two branch outcomes; confirm
        # the no-write path leaves the field untouched (A=0, C=0, E=0 is
        # in-range with a non-positive E, so the rule takes the 24 write;
        # A=0, C=0, E=0x00ff is also <= 0 signed -> 24). The no-write path is
        # the bge case with d>= -0x200, e.g. A=0, C=0, E=0x8000: d=0, the
        # bge branch is taken and d is not < -0x200.
        set_u16(obj, 0x186, 0)
        set_u16(obj, 0x32, 0)
        set_u16(obj, 0x34, 0)
        set_u16(obj, 0x198, 0x1234)
        run(obj_ptr)
        assert get_u16(obj, 0x198) == 0x1234, hex(get_u16(obj, 0x198))

    print(f"PASS: recovered i960 frame-step heading integrator ({checked} original vectors)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
