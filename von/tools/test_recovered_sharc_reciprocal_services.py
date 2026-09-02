#!/usr/bin/env python3
"""Test the recovered finite SHARC reciprocal and residual services."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    source = ROOT / "von/i960/recovered_sharc_reciprocal_services.c"
    seed_source = ROOT / "von/i960/recovered_sharc_opcode_35.c"
    with tempfile.TemporaryDirectory(prefix="von-reciprocal-services-") as directory:
        library = Path(directory) / "reciprocal_services.so"
        subprocess.run(
            ["cc", "-std=c99", "-O2", "-ffp-contract=off", "-fPIC", "-shared",
             str(source), str(seed_source), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        reciprocal = lib.recovered_sharc_opcode_03_reciprocal
        residual = lib.recovered_sharc_opcode_04_residual
        for function in (reciprocal, residual):
            function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
            function.restype = ctypes.c_uint32
        reciprocal_vectors = (
            (0x40000000, 0x3F800000, 0x40000000),
            (0x3F800000, 0x40000000, 0x3F000000),
            (0xC0000000, 0x3F800000, 0xC0000000),
        )
        for numerator, denominator, expected in reciprocal_vectors:
            actual = reciprocal(numerator, denominator)
            if actual != expected:
                raise SystemExit(f"opcode 0x03 mismatch: {actual:#010x} != {expected:#010x}")
        residual_vectors = (
            (0x3F9DF3B6, 0x3F333333, 0x00000000),
            (0xBF9DF3B6, 0x3F333333, 0x00000000),
            (0x3FD9999A, 0x3EAAAAAB, 0xB4000000),
        )
        for numerator, denominator, expected in residual_vectors:
            actual = residual(numerator, denominator)
            if actual != expected:
                raise SystemExit(f"opcode 0x04 mismatch: {actual:#010x} != {expected:#010x}")
    print("PASS: recovered finite SHARC reciprocal and residual services")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
