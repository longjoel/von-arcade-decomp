#!/usr/bin/env python3
"""Validate the finite projected predicate recovered for SHARC opcode 0x28."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_28.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode28.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-lm", "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        accepts = ctypes.CDLL(str(library)).recovered_sharc_opcode_28_accepts
        accepts.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
            ctypes.c_float, ctypes.c_float,
        ]
        accepts.restype = ctypes.c_uint32
        project = ctypes.CDLL(str(library)).recovered_sharc_opcode_28_project
        project.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
        ]
        project.restype = None

        identity = (ctypes.c_float * 12)(
            1.0, 0.0, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 1.0, 0.0, 0.0, 0.0,
        )
        unit_z = (ctypes.c_float * 3)(0.0, 0.0, 1.0)
        projected = (ctypes.c_float * 3)()
        project(unit_z, identity, projected)
        assert tuple(projected) == (0.0, 0.0, 1.0)
        assert accepts(unit_z, identity, 2.0, 2.0) == 1
        assert accepts(unit_z, identity, 1.0, 2.0) == 0
        assert accepts(unit_z, identity, 2.0, 1.0) == 0

        unit_x = (ctypes.c_float * 3)(1.0, 0.0, 0.0)
        assert accepts(unit_x, identity, 2.0, 2.0) == 0

        # The live SHARC probe shows the zero-horizontal singularity still
        # takes the visible fallback, even though its reciprocal refinement
        # produces an unordered intermediate. Negative depth also rejects at
        # the first strict LE gate.
        zero = (ctypes.c_float * 3)(0.0, 0.0, 0.0)
        assert accepts(zero, identity, 2.0, 2.0) == 0
        negative_z = (ctypes.c_float * 3)(0.0, 0.0, -1.0)
        assert accepts(negative_z, identity, 2.0, 2.0) == 0
        nan_x = (ctypes.c_float * 3)(float("nan"), 0.0, 1.0)
        assert accepts(nan_x, identity, 2.0, 2.0) == 0
        nan_depth = (ctypes.c_float * 3)(0.0, 0.0, float("nan"))
        assert accepts(nan_depth, identity, 2.0, 2.0) == 0

        translated = (ctypes.c_float * 12)(
            1.0, 0.0, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 1.0, 0.0, 0.0, 2.0,
        )
        # projected=3; radial=sqrt(1+3)=2, so lower=1 accepts and lower=2/3
        # is the strict equality boundary and rejects.
        vector = (ctypes.c_float * 3)(1.0, 0.0, 1.0)
        project(vector, translated, projected)
        assert tuple(projected) == (1.0, 0.0, 3.0)
        assert math.isclose(3.0, translated[11] + vector[2], abs_tol=1e-6)
        assert accepts(vector, translated, 1.0, 4.0) == 1
        assert accepts(vector, translated, 2.0 / 3.0, 4.0) == 0

    print("PASS: SHARC opcode-0x28 projected predicate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
