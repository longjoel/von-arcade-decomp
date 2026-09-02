#!/usr/bin/env python3
"""Validate the reusable C contract for SHARC opcode 0x46."""

from __future__ import annotations

import ctypes
import random
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode46.so"
        subprocess.run(
            [
                "cc", "-shared", "-fPIC", "-O2",
                str(ROOT / "von/i960/recovered_sharc_opcode_46.c"),
                "-o", str(library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        lib = ctypes.CDLL(str(library))
        upload = lib.recovered_sharc_opcode_46_upload
        word_array = ctypes.c_uint32 * 7
        upload.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                           ctypes.POINTER(ctypes.c_uint32)]
        upload.restype = None

        cases = [
            tuple(range(7)),
            (0x00000000, 0x80000000, 0x7FC00001, 0xFFC00002,
             0x00000001, 0x7F800000, 0xFF800000),
        ]
        generator = random.Random(0x2046)
        cases.extend(tuple(generator.getrandbits(32) for _ in range(7))
                     for _ in range(256))
        for words in cases:
            input_words = word_array(*words)
            state = word_array(*(0xA5A5A5A5 for _ in range(7)))
            upload(input_words, state)
            expected = words[:4] + (words[4] ^ 0x80000000,) + words[5:]
            assert tuple(state) == expected

    print("PASS: SHARC opcode-0x46 C state upload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
