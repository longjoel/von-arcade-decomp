#!/usr/bin/env python3
"""Exhaustively test the pure packet boundary of the 0x2a990 service."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry.c"


def expected_packet(first: int, second: int) -> tuple[int, ...]:
    return (
        5,
        16,
        20,
        first & 0xFFFF,
        21,
        second & 0xFFFF,
        26,
        0xBF34FDF4,
        0xBF34FDF4,
        0x3F34FDF4,
        6,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-geometry-service-") as directory:
        library = Path(directory) / "geometry-service.so"
        subprocess.run(
            [
                os.environ.get("CC", "cc"),
                "-shared",
                "-fPIC",
                "-O2",
                SOURCE,
                "-o",
                library,
            ],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_geometry_service_packet.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        recovered.recovered_geometry_service_packet.restype = ctypes.c_uint32

        vectors = 0
        second_values = (0, 1, 0xFFFF, 0x10000, 0xFFFFFFFF)
        for first in range(0x10000):
            for second in second_values:
                packet = (ctypes.c_uint32 * 11)()
                count = recovered.recovered_geometry_service_packet(
                    first, second, packet
                )
                actual = tuple(packet[:count])
                expected = expected_packet(first, second)
                if count != len(expected) or actual != expected:
                    raise SystemExit(
                        f"service packet mismatch first=0x{first:08x}, "
                        f"second=0x{second:08x}: {actual!r} != {expected!r}"
                    )
                vectors += 1

    print(f"PASS: {vectors:,} geometry service packet vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
