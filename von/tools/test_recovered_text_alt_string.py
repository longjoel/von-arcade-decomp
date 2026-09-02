#!/usr/bin/env python3
"""Check the alternate mode-2/mode-3 glyph-string selector."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_alt_string.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "libtext_alt_string.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
        api = ctypes.CDLL(str(library))
        function = api.recovered_text_alt_string_font_mode
        function.argtypes = [ctypes.c_char_p]
        function.restype = ctypes.c_uint32
        cases = {
            b"": 3,
            b"ABC": 3,
            b"A1_Z": 3,
            b"AbC": 2,
            b"A-z": 2,
            b"a": 3,
        }
        for text, expected in cases.items():
            actual = function(text)
            assert actual == expected, (text, actual, expected)

    print("recovered alternate text-mode vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
