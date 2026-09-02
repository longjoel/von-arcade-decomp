#!/usr/bin/env python3
"""Test the strict dual-distance predicate recovered at i960 0xdf2f4."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_dual_distance_predicate_df2f4.c"


with tempfile.TemporaryDirectory(prefix="von-distance-predicate-") as directory:
    library = Path(directory) / "distance-predicate.so"
    subprocess.run(
        ["cc", "-std=c99", "-O2", "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
        check=True,
    )
    lib = ctypes.CDLL(str(library))
    accepts = lib.recovered_geometry_dual_distance_accepts
    accepts.argtypes = [ctypes.c_float, ctypes.c_float]
    accepts.restype = ctypes.c_uint32

    for first, second, expected in (
        (0.0, 1.0, 1),
        (0.5, 0.5, 0),
        (1.0, 0.5, 0),
        (-1.0, 0.0, 1),
        (math.inf, math.inf, 0),
        (math.nan, 1.0, 0),
        (1.0, math.nan, 0),
    ):
        actual = accepts(first, second)
        if actual != expected:
            raise SystemExit(f"distance predicate mismatch: {first}, {second}")

print("recovered geometry dual-distance predicate: ok")
