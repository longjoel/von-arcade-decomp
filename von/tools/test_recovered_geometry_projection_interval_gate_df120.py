#!/usr/bin/env python3
"""Test the signed inclusive Y-window gate recovered at i960 0xdf120."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_projection_interval_gate_df120.c"


with tempfile.TemporaryDirectory(prefix="von-y-window-") as directory:
    library = Path(directory) / "y-window.so"
    subprocess.run(
        ["cc", "-std=c99", "-O2", "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
        check=True,
    )
    lib = ctypes.CDLL(str(library))
    passes = lib.recovered_geometry_projection_y_window_passes
    passes.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    passes.restype = ctypes.c_uint32

    for base in (-32768, -1, 0, 1234, 32767):
        for extent in (-2, -1, 0, 1, 2, 32767):
            lower = base
            upper = base + extent
            for selected in (lower - 1, lower, lower + 1, upper - 1, upper, upper + 1):
                expected = int(lower <= selected <= upper)
                actual = passes(selected, base, extent)
                if actual != expected:
                    raise SystemExit(
                        f"Y-window mismatch: y={selected}, base={base}, extent={extent}"
                    )

    # The extent is signed in the ROM; an inverted interval rejects every y.
    assert passes(0, 10, -1) == 0
    # Wide sums are evaluated without host signed-overflow ambiguity.
    assert passes(0x7FFFFFFF, 0x7FFFFFF0, 0x20) == 1

print("recovered geometry projection Y-window gate: ok")
