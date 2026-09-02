#!/usr/bin/env python3
"""Test the recovered SHARC 0x1b/0x1c angle-service wrappers."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]


def main() -> int:
    sources = [
        ROOT / "von/i960/recovered_sharc_opcode_1b.c",
        ROOT / "von/i960/recovered_sharc_opcode_1c.c",
        ROOT / "von/i960/recovered_sharc_helper_20dbe.c",
    ]
    with tempfile.TemporaryDirectory(prefix="von-opcode-1bc-") as directory:
        library_path = pathlib.Path(directory) / "opcode_1bc.so"
        subprocess.run(
            ["cc", "-std=c99", "-O2", "-ffp-contract=off", "-fPIC", "-shared",
             *(str(source) for source in sources), "-o", str(library_path)],
            check=True,
        )
        library = ctypes.CDLL(str(library_path))
        sine = library.recovered_sharc_opcode_1b
        cosine = library.recovered_sharc_opcode_1c
        sine.argtypes = [ctypes.c_uint32]
        cosine.argtypes = [ctypes.c_uint32]
        sine.restype = cosine.restype = ctypes.c_uint32
        expected_sine = {
            0x0000: 0x00000000,
            0x4000: 0x3F800000,
            0x7FFF: 0xB3BBBD00,
            0x8000: 0x38C92EEF,
        }
        expected_cosine = {
            0x0000: 0x3F7FFFFF,
            0x4000: 0xB8492EEF,
            0x7FFF: 0xBF7FFFFF,
            0x8000: 0xBF7FFFFF,
        }
        for angle, expected in expected_sine.items():
            actual = sine(angle)
            if actual != expected:
                raise SystemExit(f"0x1b angle={angle:#x}: {actual:#010x} != {expected:#010x}")
        for angle, expected in expected_cosine.items():
            actual = cosine(angle)
            if actual != expected:
                raise SystemExit(f"0x1c angle={angle:#x}: {actual:#010x} != {expected:#010x}")
    print("PASS: recovered SHARC 0x1b/0x1c angle-service wrappers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
