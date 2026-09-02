#!/usr/bin/env python3
"""Check the recovered 0x1de80 tile-block writer."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_tile_block.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "libtext_tile_block.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
        api = ctypes.CDLL(str(library))
        function = api.recovered_text_write_tile_block
        function.argtypes = [
            ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(ctypes.c_uint16),
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ]
        function.restype = None

        destination = (ctypes.c_uint16 * (64 * 8))(*([0x1234] * (64 * 8)))
        source = (ctypes.c_uint16 * 12)(*range(12))
        function(destination, source, 3, 2, 4, 3)
        for y in range(3):
            for x in range(4):
                assert destination[(2 + y) * 64 + 3 + x] == 0x8000 | (y * 4 + x)
        assert destination[2 * 64 + 2] == 0x1234
        assert destination[5 * 64 + 7] == 0x1234

        empty = (ctypes.c_uint16 * (64 * 2))(*([0x5678] * (64 * 2)))
        function(empty, source, 0, 0, 0, 3)
        function(empty, source, 0, 0, 3, 0)
        assert all(value == 0x5678 for value in empty)

    print("recovered text tile-block vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
