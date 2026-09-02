#!/usr/bin/env python3
"""Test the recovered 0xe2130 video asset routing plan."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_video_setup.c"


class Asset(ctypes.Structure):
    _fields_ = [("tile", ctypes.c_uint32), ("source", ctypes.c_uint32)]


class Plan(ctypes.Structure):
    _fields_ = [
        ("bank", ctypes.c_int),
        ("assets", Asset * 14),
        ("published_base", ctypes.c_uint32),
        ("published_offsets", ctypes.c_uint32 * 5),
        ("published_sentinel", ctypes.c_uint32),
    ]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-video-setup-") as directory:
        library = Path(directory) / "video-setup.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        function = recovered.recovered_video_setup_plan
        function.argtypes = [*(ctypes.c_uint32 for _ in range(5)), ctypes.POINTER(Plan)]
        function.restype = None

        for values, expected_bank, expected_sources in [
            ((0, 0, 99, 99, 99), 0, [0x02FB3D90, 0x02FB3E50, 0x02FB4990, 0x02FB4A50]),
            ((1, 2, 0, 7, 7), 0, [0x02FB3D90, 0x02FB3E50, 0x02FB4990, 0x02FB4A50]),
            ((1, 2, 0, 6, 7), 1, [0x02FB3F10, 0x02FB3FD0, 0x02FB4B10, 0x02FB4BD0]),
            ((1, 1, 0, 0, 0), 1, [0x02FB3F10, 0x02FB3FD0, 0x02FB4B10, 0x02FB4BD0]),
        ]:
            plan = Plan()
            function(*values, ctypes.byref(plan))
            if plan.bank != expected_bank:
                raise SystemExit(f"bank mismatch for {values}")
            if [asset.tile for asset in plan.assets] != [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 25, 27, 29]:
                raise SystemExit("tile sequence mismatch")
            if [asset.source for asset in plan.assets[:4]] != expected_sources:
                raise SystemExit(f"bank source mismatch for {values}")
            if plan.published_base != 0x02F8D890 or list(plan.published_offsets) != [0x60C0, 0xC180, 0x12240, 0x18300, 0x1E3C0]:
                raise SystemExit("published pointer layout mismatch")
            if plan.published_sentinel != 0xFF:
                raise SystemExit("published sentinel mismatch")

    print("PASS: 0xe2130 video bank predicate, asset list, and published pointer layout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
