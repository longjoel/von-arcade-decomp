#!/usr/bin/env python3
"""Verify the recovered 0x75d90 stage selector against live goldens.

Vectors come from the fresh-NVRAM replay of
von/captures/vonj-20260907T211227Z/inp/stage3-fleet: mode byte 2 in
every setup window (probe75), ordinals/cells from the trace, outputs
from spawn RAM dumps d1-d4 (0x504dbc 20/1c/1c/80, 0x504dc0
70/6c/6c/d0, d88 0, d8c/d90 ffffffff, constants d60 43200000,
d78/d84/dac/db0 1, db8 5).
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_stage_selector_75d90.c"


TAIL_FIELDS = (
    "d64 d68 d6c d70 d74 d7c d80 d88 dc4 d8c d90 "
    "d94 d98 d9c da0 da4 da8 db4 dc8 dcc dd0 "
    "d60 d78 d84 dac db0 db8"
).split()


class Tail(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in TAIL_FIELDS]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-stage-selector-") as directory:
        library = Path(directory) / "stage-selector.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
             str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        lib.stage_selector_g7.argtypes = [ctypes.c_uint32]
        lib.stage_selector_g7.restype = ctypes.c_uint32
        lib.stage_selector_index.argtypes = [ctypes.c_uint32] * 4
        lib.stage_selector_index.restype = ctypes.c_uint32
        lib.stage_selector_g6.argtypes = [ctypes.c_uint32] * 2
        lib.stage_selector_g6.restype = ctypes.c_uint32
        lib.stage_selector_stamp.argtypes = [
            ctypes.c_uint32] * 6 + [ctypes.POINTER(ctypes.c_uint32)]
        lib.stage_selector_stamp.restype = ctypes.c_uint32
        lib.stage_selector_tail.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32,
            ctypes.POINTER(Tail)]
        lib.stage_selector_tail.restype = None

        g7 = lib.stage_selector_g7
        assert (g7(0), g7(1), g7(2), g7(3), g7(4), g7(255)) == \
            (4, 8, 30, 2, 4, 4), "g7 arms"

        index = lib.stage_selector_index
        assert index(4, 0, 0, 0) == 0, "S1 index"
        assert index(4, 0, 0, 3) == 3, "S4 index"
        assert index(1, 99, 0, 2) == 2, "f4 gate"
        assert index(4, 7, 0, 1) == 8, "a94 passthrough"
        assert index(4, 0, 5, 1) == 2, "a6c increment"
        assert index(4, 0, 0xFFFFFFFF, 1) == 1, "a6c sign"

        g6 = lib.stage_selector_g6
        assert (g6(0, 0), g6(2, 0), g6(3, 0), g6(4, 0), g6(5, 0),
                g6(6, 0)) == (1, 8, 32, 64, 64, 99), "table arms"
        assert (g6(1, 1), g6(1, 2), g6(1, 5)) == (2, 2, 2), "sub 2-arm"
        assert (g6(1, 0), g6(1, 4), g6(1, 9)) == (3, 3, 3), "sub 3-arm"

        dc0 = ctypes.c_uint32(0)
        stamp = lib.stage_selector_stamp
        # (g6, divword, expected dbc, expected dc0, label)
        for g6v, word, dbc, dc, label in (
                (1, 30, 3, 83, "S1"),
                (2, 120, 12, 0x5C, "S2"),
                (8, 320, 32, 0x70, "S3 first"),
                (8, 280, 28, 0x6C, "S3 continue"),
                (32, 1280, 128, 0xD0, "S4"),
                (64, 2560, 256, 300, "S5 clamp")):
            got = stamp(g6v, 30, 2, 2, 0, word, ctypes.byref(dc0))
            assert (got, dc0.value) == (dbc, dc), (label, got, dc0.value)
        # takeover paths yield the raw product (dc0 clamps at 300)
        got = stamp(8, 30, 3, 2, 0, 320, ctypes.byref(dc0))
        assert (got, dc0.value) == (240, 300), (got, dc0.value)
        got = stamp(8, 30, 2, 2, 1, 320, ctypes.byref(dc0))
        assert (got, dc0.value) == (240, 300), (got, dc0.value)

        tail = Tail()
        lib.stage_selector_tail(0, 0, ctypes.byref(tail))
        for name in TAIL_FIELDS:
            value = getattr(tail, name)
            if name in ("d8c", "d90"):
                assert value == 0xFFFFFFFF, (name, value)
            elif name == "d60":
                assert value == 0x43200000, (name, value)
            elif name in ("d78", "d84", "dac", "db0"):
                assert value == 1, (name, value)
            elif name == "db8":
                assert value == 5, (name, value)
            else:
                assert value == 0, (name, value)
        print("PASS: stage selector truth table (S1-S5, takeover, tail)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
