#!/usr/bin/env python3
"""Exhaustively test the host-buildable recovered runtime math leaves."""

from __future__ import annotations

import ctypes
import os
import random
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_runtime_math.c"
MASK31 = 0x7FFFFFFF
MULTIPLIER = 0x5D588B65


def random_reference(state: int) -> int:
    product = state * MULTIPLIER
    low = product & 0xFFFFFFFF
    high = (product >> 32) & 0xFFFFFFFF
    return (low + (high << 1) + (low >> 31)) & MASK31


def band_reference(raw: int) -> int:
    value = ctypes.c_int16(raw).value
    if value >= 0:
        if value <= 0x038D:
            return 0
        if value <= 0x1554:
            return 1
        if value <= 0x3FFF:
            return 2
        if value <= 0x5FFF:
            return 3
        return 4
    if value < -0x6000:
        return 5
    if value < -0x4000:
        return 6
    if value < -0x1555:
        return 7
    if value < -0x038E:
        return 8
    return 9


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-runtime-math-") as directory:
        library = Path(directory) / "runtime-math.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_random_step.argtypes = [ctypes.c_uint32]
        recovered.recovered_random_step.restype = ctypes.c_uint32
        recovered.recovered_signed_band.argtypes = [ctypes.c_uint32]
        recovered.recovered_signed_band.restype = ctypes.c_uint32

        generator = random.Random(0x960)
        random_states = [0, 1, 2, 3, 0x01234567, 0x40000000, MASK31]
        random_states.extend(generator.randrange(MASK31 + 1) for _ in range(10_000))
        for state in random_states:
            actual = recovered.recovered_random_step(state)
            expected = random_reference(state)
            if actual != expected:
                raise SystemExit(
                    f"PRNG mismatch at 0x{state:08x}: 0x{actual:08x} != 0x{expected:08x}"
                )

        for raw in range(0x10000):
            actual = recovered.recovered_signed_band(raw)
            expected = band_reference(raw)
            if actual != expected:
                raise SystemExit(f"band mismatch at 0x{raw:04x}: {actual} != {expected}")

    print("PASS: 10,007 PRNG vectors and all 65,536 signed-band inputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
