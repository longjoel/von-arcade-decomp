#!/usr/bin/env python3
"""Contract test for the deterministic geometry staging fill."""

from pathlib import Path
import ctypes
import os
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-geometry-fill-") as directory:
        library = Path(directory) / "geometry.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", str(SOURCE),
             "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_geometry_program_fill.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, ctypes.c_uint32]
        recovered.recovered_geometry_program_fill.restype = None

        words = 0x8000
        staging = (ctypes.c_uint32 * (words + 1))(*([0xDEADBEEF] * (words + 1)))
        recovered.recovered_geometry_program_fill(staging, words, 0x07800F0F)
        if any(value != 0x07800F0F for value in staging[:words]):
            raise SystemExit("staging fill value mismatch")
        if staging[words] != 0xDEADBEEF:
            raise SystemExit("staging fill exceeded the declared word count")

    print(f"PASS: {words:,} geometry staging words filled in order")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
