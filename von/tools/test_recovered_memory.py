#!/usr/bin/env python3
"""Check the recovered i960 forward-copy primitive."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_memory.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-memory-") as directory:
        library = Path(directory) / "memory.so"
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
        recovered.recovered_memory_copy_forward.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        recovered.recovered_memory_copy_forward.restype = None

        vectors = 0
        for source_alignment in range(16):
            for destination_alignment in range(16):
                for length in range(129):
                    source = (ctypes.c_ubyte * 160)()
                    destination = (ctypes.c_ubyte * 160)()
                    for index in range(160):
                        source[index] = (index * 37 + 11) & 0xFF
                        destination[index] = 0xA5
                    recovered.recovered_memory_copy_forward(
                        ctypes.byref(destination, destination_alignment),
                        ctypes.byref(source, source_alignment),
                        length,
                    )
                    actual = bytes(destination)
                    expected = bytearray(b"\xA5" * 160)
                    expected[destination_alignment:destination_alignment + length] = (
                        bytes(source[source_alignment:source_alignment + length])
                    )
                    if actual != bytes(expected):
                        raise SystemExit(
                            "copy mismatch "
                            f"source_alignment={source_alignment} "
                            f"destination_alignment={destination_alignment} length={length}"
                        )
                    vectors += 1

    print(f"PASS: {vectors:,} forward-copy alignment and length vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
