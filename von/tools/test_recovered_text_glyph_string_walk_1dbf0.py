#!/usr/bin/env python3
"""Check the 0x1dbf0 NUL walk and fixed 0x1d6a0 callee connection."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_glyph_string_walk_1dbf0.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-glyph-string-walk-") as directory:
        library = Path(directory) / "glyph-string-walk.so"
        subprocess.run([
            os.environ.get("CC", "cc"), "-shared", "-fPIC", str(SOURCE),
            "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))
        walk = recovered.recovered_text_glyph_string_walk_1dbf0
        walk.argtypes = [ctypes.c_char_p,
                         ctypes.POINTER(ctypes.c_uint32),
                         ctypes.POINTER(ctypes.c_uint32)]
        walk.restype = ctypes.c_uint32
        checked = 0
        for text in (b"", b"A", b"ABC", b"A\x00ignored", b"\xff\x01\x00"):
            count = ctypes.c_uint32()
            callee = ctypes.c_uint32()
            if walk(text, ctypes.byref(count), ctypes.byref(callee)) != 1:
                raise SystemExit("glyph string walk plan failed")
            expected_count = len(text.split(b"\x00", 1)[0])
            if (count.value, callee.value) != (expected_count, 0x1d6a0):
                raise SystemExit("glyph string walk connection mismatch")
            checked += 1
    print(f"PASS: {checked} 0x1dbf0 glyph-string walk vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
