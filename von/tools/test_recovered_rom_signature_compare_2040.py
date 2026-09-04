#!/usr/bin/env python3
"""Test the exact ROM signature comparator at i960 0x2040."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_rom_signature_compare_2040.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-rom-signature-") as directory:
        library = Path(directory) / "signature.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        check = recovered.recovered_rom_signature_compare_2040
        check.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
        check.restype = ctypes.c_uint32
        for accepted in (b"SEGA", b"S32A"):
            candidate = (ctypes.c_uint8 * 4).from_buffer_copy(accepted)
            assert check(candidate) == 1
        for rejected in (b"SEGB", b"XXXX", b"S32B"):
            candidate = (ctypes.c_uint8 * 4).from_buffer_copy(rejected)
            assert check(candidate) == 0
    print("PASS: 0x2040 ROM signature comparator")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
