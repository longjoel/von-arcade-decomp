#!/usr/bin/env python3
"""Test the deterministic geometry buffer and four-batch contract."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

from verify_geometry_buffer import expected


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry.c"


def main() -> int:
    values = expected()
    if len(values) != 0x2000:
        raise SystemExit(f"geometry buffer length mismatch: {len(values)}")
    if values[:4] != [0, 0, 0, 0]:
        raise SystemExit("geometry buffer initial words mismatch")
    if values[-2:] != [0x7F7F7F7F, 0x7F7F7F7F]:
        raise SystemExit("geometry buffer terminal words mismatch")
    for batch in range(4):
        if len(values[batch * 0x800:(batch + 1) * 0x800]) != 0x800:
            raise SystemExit(f"geometry batch {batch} length mismatch")

    with tempfile.TemporaryDirectory(prefix="von-geometry-buffer-c-") as directory:
        library = Path(directory) / "geometry.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", str(SOURCE),
             "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        prepare = recovered.recovered_geometry_buffer_prepare
        prepare.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        prepare.restype = None
        output = (ctypes.c_uint32 * len(values))()
        prepare(output)
        actual = list(output)
        if actual != values:
            for index, (got, want) in enumerate(zip(actual, values)):
                if got != want:
                    raise SystemExit(
                        f"C geometry buffer mismatch at 0x{index:04x}: "
                        f"got {got:08x}, expected {want:08x}"
                    )
            raise SystemExit("C geometry buffer length mismatch")

    print("PASS: geometry buffer Python/C models and four-batch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
