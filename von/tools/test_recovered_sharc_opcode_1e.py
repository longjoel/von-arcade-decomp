#!/usr/bin/env python3
"""Test the recovered SHARC opcode-0x1e cosine-times-float contract."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    source = ROOT / "von/i960/recovered_sharc_opcode_1e.c"
    helper = ROOT / "von/i960/recovered_sharc_helper_20dbe.c"
    with tempfile.TemporaryDirectory(prefix="von-opcode-1e-") as directory:
        library = Path(directory) / "opcode_1e.so"
        subprocess.run(
            ["cc", "-std=c99", "-O2", "-ffp-contract=off", "-fPIC", "-shared",
             str(source), str(helper), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library)).recovered_sharc_opcode_1e
        recovered.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        recovered.restype = ctypes.c_uint32
        vectors = (
            (0x00000000, 0x3F800000, 0x3F7FFFFF),
            (0x00004000, 0x40000000, 0xB8C92EEF),
            (0x00002000, 0x3F800000, 0x3F3503D8),
        )
        for angle, multiplier, expected in vectors:
            actual = recovered(angle, multiplier)
            if actual != expected:
                raise SystemExit(
                    f"opcode 0x1e mismatch angle={angle:#x} multiplier={multiplier:#x}: "
                    f"{actual:#010x} != {expected:#010x}"
                )
    print("PASS: recovered SHARC opcode-0x1e cosine-times-float contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
