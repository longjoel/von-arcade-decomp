#!/usr/bin/env python3
"""Check the literal mode-bit arms at i960 0x784c8."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_status_dispatch_784c8.c"


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-status.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_status_should_set_784c8
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = ctypes.c_uint32

    for selector in range(10):
        for mode_bits in range(8):
            if selector in (0, 6):
                expected = bool(mode_bits & 0x2)
            elif selector in (1, 3):
                expected = bool(mode_bits & 0x4)
            else:
                expected = bool(mode_bits & 0x6)
            assert function(selector, mode_bits) == expected

    for selector in (10, 0xffffffff):
        assert function(selector, 0x6) == 0

print("recovered 0x784c8 transition-status vectors: ok")
