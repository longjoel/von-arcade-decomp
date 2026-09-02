#!/usr/bin/env python3
"""Test the recovered normalized cross-product model for SHARC opcode 0x0b."""

import ctypes
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_0b.c"
SEED_SOURCE = ROOT / "von/i960/recovered_sharc_opcode_1f.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-0b-") as directory:
        library = Path(directory) / "libopcode_0b.so"
        subprocess.run(["cc", "-std=c99", "-O2", "-fPIC", "-shared",
                        str(SOURCE), str(SEED_SOURCE), "-lm", "-o", str(library)],
                       check=True)
        lib = ctypes.CDLL(str(library))
        normalize = lib.recovered_sharc_opcode_0b_normalized_cross
        normalize.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                              ctypes.POINTER(ctypes.c_uint32)]
        normalize.restype = None
        vectors = (
            ((0x40400000, 0x40800000, 0x41400000, 0, 0, 0,
              0x3f800000, 0x3f800000, 0),
             (0xbf34b4b4, 0x3f34b4b4, 0xbd70f0f0)),
            ((0, 0, 0, 0, 0, 0, 0, 0, 0),
             (0xffffffff, 0xffffffff, 0xffffffff)),
            ((0, 0x3f800000, 0, 0, 0, 0, 0x3f800000, 0, 0),
             (0x00000000, 0x00000000, 0xbf800000)),
            ((0x7fc00000, 0, 0, 0, 0, 0, 0x3f800000, 0, 0),
             (0xffffffff, 0xffffffff, 0xffffffff)),
            ((0x7f800000, 0, 0, 0, 0, 0, 0x3f800000, 0, 0),
             (0xffffffff, 0xffffffff, 0xffffffff)),
            ((0x00000001, 0, 0, 0, 0, 0, 0x3f800000, 0, 0),
             (0xffffffff, 0xffffffff, 0xffffffff)),
        )
        for values, expected in vectors:
            input_words = (ctypes.c_uint32 * 9)(*values)
            output_words = (ctypes.c_uint32 * 3)()
            normalize(input_words, output_words)
            actual = tuple(output_words)
            if actual != expected:
                raise SystemExit(f"opcode 0x0b mismatch: {values!r} -> "
                                 f"{tuple(f'0x{x:08x}' for x in actual)}, "
                                 f"expected {tuple(f'0x{x:08x}' for x in expected)}")
    print("recovered SHARC opcode-0b normalized cross-product vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
