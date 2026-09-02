#!/usr/bin/env python3
"""Validate the reusable C contract for SHARC opcode 0x48."""

from __future__ import annotations

import ctypes
import random
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode48.so"
        subprocess.run(
            [
                "cc", "-shared", "-fPIC", "-O2",
                str(ROOT / "von/i960/recovered_sharc_opcode_48.c"),
                "-o", str(library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        lib = ctypes.CDLL(str(library))
        upload = lib.recovered_sharc_opcode_48_upload
        word_array = ctypes.c_uint32 * 5
        upload.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                           ctypes.POINTER(ctypes.c_uint32)]
        upload.restype = None

        cases = [tuple(range(5)),
                 (0x00000000, 0x80000000, 0x7FC00001,
                  0x7F800000, 0xFFFFFFFF)]
        generator = random.Random(0x2048)
        cases.extend(tuple(generator.getrandbits(32) for _ in range(5))
                     for _ in range(256))
        for words in cases:
            input_words = word_array(*words)
            state = word_array(*(0xA5A5A5A5 for _ in range(5)))
            upload(input_words, state)
            assert tuple(state) == words

    print("PASS: SHARC opcode-0x48 C state upload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
