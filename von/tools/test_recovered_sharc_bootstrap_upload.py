#!/usr/bin/env python3
"""Contract test for the bounded SHARC bootstrap FIFO copy."""

from pathlib import Path
import ctypes
import os
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-bootstrap-") as directory:
        library = Path(directory) / "geometry.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", str(SOURCE),
             "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_sharc_bootstrap_copy.argtypes = [
            ctypes.POINTER(ctypes.c_uint16),
            ctypes.POINTER(ctypes.c_uint16),
            ctypes.c_uint32,
        ]
        recovered.recovered_sharc_bootstrap_copy.restype = None

        words = 0x2B1E
        source = (ctypes.c_uint16 * words)(
            *(((index * 0x31) ^ 0x5A5A) & 0xFFFF for index in range(words))
        )
        fifo = (ctypes.c_uint16 * (words + 1))(*([0xBEEF] * (words + 1)))
        recovered.recovered_sharc_bootstrap_copy(fifo, source, words)
        for index in range(words):
            if fifo[index] != source[index]:
                raise SystemExit(f"FIFO mismatch at index {index}")
        if fifo[words] != 0xBEEF:
            raise SystemExit("FIFO copy exceeded the declared word count")

    print(f"PASS: {words:,} SHARC bootstrap halfwords copied in order")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
