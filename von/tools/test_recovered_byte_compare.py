#!/usr/bin/env python3
"""Check the recovered 0xf5c58 byte-range comparison contract."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_byte_compare.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "libbyte_compare.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
            check=True,
        )
        api = ctypes.CDLL(str(library))
        function = api.recovered_byte_compare
        function.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
        function.restype = ctypes.c_uint32

        cases = [
            (b"", b"", 0, 0),
            (b"abc", b"abc", 3, 0),
            (b"abc", b"abd", 3, 0xFFFFFFFF),
            (b"abd", b"abc", 3, 1),
            (b"abc", b"abd", 2, 0),
            (bytes([0x00, 0xFF]), bytes([0x00, 0x01]), 2, 0xFE),
        ]
        for left, right, length, expected in cases:
            left_buffer = ctypes.create_string_buffer(left)
            right_buffer = ctypes.create_string_buffer(right)
            actual = function(left_buffer, right_buffer, length)
            assert actual == expected, (left, right, length, actual, expected)

    print("recovered byte-compare vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
