#!/usr/bin/env python3
"""Test the recovered signed-angle model for SHARC opcode 0x0f."""

import ctypes
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_0f.c"
HELPER_SOURCE = ROOT / "von/i960/recovered_sharc_helper_20d68_candidate.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-0f-") as directory:
        library = Path(directory) / "libopcode_0f.so"
        subprocess.run(["cc", "-std=c99", "-O2", "-ffp-contract=off", "-fPIC", "-shared",
                        str(SOURCE), str(HELPER_SOURCE), "-o", str(library)], check=True)
        lib = ctypes.CDLL(str(library))
        angle = lib.recovered_sharc_opcode_0f_angle
        angle.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                          ctypes.POINTER(ctypes.c_uint32)]
        angle.restype = None
        vectors = (
            ((0, 0, 0, 0), 0x00000000),
            ((0x3f800000, 0, 0, 0), 0x00000000),
            ((0, 0x3f800000, 0, 0), 0x00003fff),
            ((0x3f800000, 0x3f800000, 0, 0), 0x00001fff),
            ((0, 0xbf800000, 0, 0), 0xffffc000),
            ((0xbf800000, 0, 0, 0), 0x00007fff),
            # Finite-ratio outputs cross-checked against the 0x20d68 runtime
            # sweep, after the caller's 32767/pi scale and FIX.
            ((0x40000000, 0x3f800000, 0, 0), 0x000012e3),
            ((0x3f800000, 0x40000000, 0, 0), 0x00002d1b),
            ((0xc0000000, 0x3f800000, 0, 0), 0x00006d1b),
            ((0x3f800000, 0xc0000000, 0, 0), 0xffffd2e5),
            ((0x40800000, 0x3f800000, 0, 0), 0x000009fb),
            ((0x3f800000, 0x40800000, 0, 0), 0x00003604),
        )
        for values, expected in vectors:
            input_words = (ctypes.c_uint32 * 4)(*values)
            output_word = (ctypes.c_uint32 * 1)()
            angle(input_words, output_word)
            if output_word[0] != expected:
                raise SystemExit(f"opcode 0x0f mismatch: {values!r} -> "
                                 f"0x{output_word[0]:08x}, expected 0x{expected:08x}")
    print("recovered SHARC opcode-0f signed-angle vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
