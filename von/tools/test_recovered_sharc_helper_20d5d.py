#!/usr/bin/env python3
"""Test the recovered external table-base derivation used by helper 0x20d5d."""

import ctypes
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_helper_20d5d.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-helper-20d5d-") as directory:
        library = Path(directory) / "libhelper.so"
        subprocess.run(["cc", "-std=c99", "-O2", "-fPIC", "-shared",
                        str(SOURCE), "-o", str(library)], check=True)
        lib = ctypes.CDLL(str(library))
        derive = lib.recovered_sharc_helper_20d5d_derive
        derive.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                           ctypes.POINTER(ctypes.c_uint32)]
        derive.restype = None
        for values, expected in (((0, 0, 0), (0x01c00000, 0x01c00000)),
                                 ((7, 0x120, 0x340),
                                  (0x01c00120, 0x01c00340))):
            output = (ctypes.c_uint32 * 2)()
            derive(*values, output)
            if tuple(output) != expected:
                raise SystemExit(f"helper 0x20d5d mismatch: {values} -> "
                                 f"{tuple(output)}, expected {expected}")
    print("recovered SHARC helper-0x20d5d table-base vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
