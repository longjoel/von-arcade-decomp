#!/usr/bin/env python3
"""Test the pure timing split extracted from the 0x786d0 action arm."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_timing_variant.c"


def float_bits(value: float) -> int:
    import struct

    return struct.unpack("<I", struct.pack("<f", value))[0]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-timing-variant-") as directory:
        library = Path(directory) / "timing-variant.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-lm", "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        route = recovered.recovered_timing_variant_route
        route.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        route.restype = ctypes.c_int

        for current, threshold, expected in ((10.0, 5.0, 1), (5.0, 5.0, 1), (4.0, 5.0, 2)):
            if route(float_bits(current), float_bits(threshold)) != expected:
                raise SystemExit(f"timing route mismatch for {current} >= {threshold}")
        if route(float_bits(float("nan")), float_bits(5.0)) != 0:
            raise SystemExit("NaN timing rejection mismatch")

        class Plan(ctypes.Structure):
            _fields_ = [("route", ctypes.c_int),
                        ("status_write", ctypes.c_uint32)]

        plan = recovered.recovered_timing_variant_plan
        plan.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32]
        plan.restype = Plan
        composed = plan(float_bits(4.0), float_bits(5.0), 3, 0x4)
        if (composed.route, composed.status_write) != (2, 1):
            raise SystemExit("composed timing/status plan mismatch")
        composed = plan(float_bits(5.0), float_bits(5.0), 0, 0x4)
        if (composed.route, composed.status_write) != (1, 0):
            raise SystemExit("selector-0 mode-bit composition mismatch")

    print("PASS: 0x786d0 normalized timing split and NaN guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
