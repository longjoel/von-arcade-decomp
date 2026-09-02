#!/usr/bin/env python3
"""Validate the normal weighted-normalization path recovered for opcode 0x27."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_27.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode27.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-lm", "-o", str(library)],
            check=True,
            capture_output=True,
            text=True,
        )
        lib = ctypes.CDLL(str(library))
        normalize = lib.recovered_sharc_opcode_27_normalized_lanes
        normalize.argtypes = [ctypes.c_float] * 4 + [
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
        normalize.restype = ctypes.c_uint32
        state = (ctypes.c_float * 5)(1.0, 0.0, 1.0, 10.0, 0.0)
        output = (ctypes.c_float * 3)()
        assert normalize(0.0, 0.0, 1.0, 1.0, state, output) == 1
        assert math.isclose(output[0], 1.0 / math.sqrt(2.0), abs_tol=1e-6)
        assert math.isclose(output[1], 1.0 / math.sqrt(2.0), abs_tol=1e-6)
        assert output[2] == 1.0

        tight_state = (ctypes.c_float * 5)(1.0, 0.0, 1.0, 1.0, 0.0)
        assert normalize(0.0, 0.0, 1.0, 1.0, tight_state, output) == 0
        assert tuple(output) == (0.0, 0.0, 0.0)

        uploaded = lib.recovered_sharc_opcode_27_uploaded_state
        uploaded.argtypes = [ctypes.c_float, ctypes.c_float,
                             ctypes.POINTER(ctypes.c_float),
                             ctypes.POINTER(ctypes.c_float)]
        uploaded.restype = ctypes.c_uint32
        asymmetric = (ctypes.c_float * 5)(4.0, 123.0, 9.0, 20.0, -456.0)
        assert uploaded(1.0, 3.0, asymmetric, output) == 1
        magnitude = math.sqrt(4.0 * 3.0 * 3.0 + 9.0 * 6.0 * 6.0)
        assert math.isclose(output[0], 3.0 / magnitude, abs_tol=1e-6)
        assert math.isclose(output[1], 6.0 / magnitude, abs_tol=1e-6)
        assert output[2] == 1.0

        nan_input = (ctypes.c_float * 5)(1.0, 0.0, 1.0, 10.0, 0.0)
        assert uploaded(float("nan"), 0.0, nan_input, output) == 0
        assert tuple(output) == (0.0, 0.0, 0.0)
        nan_threshold = (ctypes.c_float * 5)(1.0, 0.0, 1.0, float("nan"), 0.0)
        assert uploaded(0.0, 0.0, nan_threshold, output) == 0
        assert tuple(output) == (0.0, 0.0, 0.0)

    print("PASS: SHARC opcode-0x27 normalized lanes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
