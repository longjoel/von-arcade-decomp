#!/usr/bin/env python3
"""Test the recovered pointer publication performed by SHARC opcode 0x0d."""

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_0d.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-0d-") as directory:
        library = Path(directory) / "libopcode_0d.so"
        subprocess.run(["cc", "-std=c99", "-O2", "-fPIC", "-shared",
                        str(SOURCE), "-o", str(library)], check=True)
        lib = ctypes.CDLL(str(library))
        publish = lib.recovered_sharc_opcode_0d_publish
        publish.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        publish.restype = None
        vectors = (
            (0x00000000, 0x00000000, 0x00000000,
             (0x01c00000, 0x01c00000)),
            (0x00000010, 0x00000010, 0x00000020,
             (0x01c00010, 0x01c00020)),
            (0x00ffffff, 0xffffffff, 0x80000000,
             (0x01bfffff, 0x81c00000)),
        )
        for base, word_10, word_20, expected in vectors:
            output = (ctypes.c_uint32 * 2)()
            publish(base, word_10, word_20, output)
            actual = tuple(output)
            if actual != expected:
                raise SystemExit(f"opcode 0x0d mismatch: {actual!r} != {expected!r}")
    print("recovered SHARC opcode-0d pointer publication: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
