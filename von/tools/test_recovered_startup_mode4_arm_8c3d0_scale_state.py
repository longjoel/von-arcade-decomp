#!/usr/bin/env python3
"""Vectors for the 0x8c3d0 selector-1 scale/state checkpoint."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8c3d0_scale_state.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "counter_51c984", "computed_scale", "state_51c94c", "rolling_51c958",
        "rolling_51c95c", "rolling_51c960", "counter_limit", "short_scan_path",
        "negative_rolling_path", "clamped_rolling_51c95c", "scale_constant",
        "compare_constant", "clamp_constant", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8c3d0:.*ld.*0x51c984,g7", r"8c3d8:.*lda.*0xffffff88\(g7\)",
        r"8c3e0:.*cvtir.*g4,fp0", r"8c3e8:.*lda.*0x403e0000,g5",
        r"8c42c:.*st.*g4,0x51c94c", r"8c440:.*shlo.*3,15,r8",
        r"8c444:.*cmpible.*g7,r8,0x8c4dc", r"8c4c0:.*st.*r9,0x51c95c",
        r"8c4c8:.*st.*g4,0x51c958", r"8c4d0:.*st.*g5,0x51c960",
        r"8c510:.*ld.*0x51c95c,g4", r"8c528:.*cmprl.*fp0,r8",
        r"8c530:.*lda.*0x41200000,r9", r"8c538:.*st.*r9,0x51c95c"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "state.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8c3d0_scale_state
        function.argtypes = [ctypes.c_uint32] * 5
        function.restype = Result
        short = function(120, 0x12, 1, 0x3f800000, 2)
        assert (short.state_51c94c, short.short_scan_path, short.negative_rolling_path,
                short.clamped_rolling_51c95c) == (0x12, 1, 0, 0x3f800000)
        long = function(121, 0x34, 1, 0x80000000, 2)
        assert (long.short_scan_path, long.negative_rolling_path, long.rolling_51c95c,
                long.clamped_rolling_51c95c) == (0, 1, 0x41200000, 0x41200000)
    print("recovered 0x8c3d0 scale/state vectors: ok")


if __name__ == "__main__":
    main()
