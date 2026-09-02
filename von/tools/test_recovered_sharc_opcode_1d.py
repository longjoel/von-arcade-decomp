#!/usr/bin/env python3
"""Test the recovered SHARC opcode-0x1d angle-times-float contract."""

from __future__ import annotations

import ctypes
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def bits(value: float) -> int:
    return struct.unpack(">I", struct.pack(">f", value))[0]


def main() -> int:
    source = ROOT / "von/i960/recovered_sharc_opcode_1d.c"
    helper = ROOT / "von/i960/recovered_sharc_helper_20dbe.c"
    with tempfile.TemporaryDirectory(prefix="von-opcode-1d-") as directory:
        library = Path(directory) / "opcode_1d.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(source), str(helper), "-lm", "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library)).recovered_sharc_opcode_1d
        recovered.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        recovered.restype = ctypes.c_uint32
        vectors = (
            (0x00004000, 0x3F800000, 0x3F800000),
            (0x00002000, 0x40000000, 0x3FB50610),
            (0xFFFFC000, 0x3F000000, 0xBF000000),
            (0x00007FFF, 0x3F800000, 0xB3BBBD00),
        )
        for angle, multiplier, expected in vectors:
            actual = recovered(angle, multiplier)
            if actual != expected:
                raise SystemExit(
                    f"opcode 0x1d mismatch angle={angle:#x} multiplier={multiplier:#x}: "
                    f"{actual:#010x} != {expected:#010x}"
                )
    print("PASS: recovered SHARC opcode-0x1d angle-times-float contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
