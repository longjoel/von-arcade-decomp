#!/usr/bin/env python3
"""Check the state-4 selector body at i960 0x7d4e8."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_selector_body_4_7d4e8.c"


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-selector-body-4.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_selector_body_4_7d4e8
    function.argtypes = [ctypes.c_uint32] * 6
    function.restype = ctypes.c_uint32

    assert function(2, 0, 0, 0, 0, 1) == 0x7D5F4
    assert function(0, 0, 1, 1, 1, 0) == 0x7D654
    assert function(0, 1, 0, 1, 1, 0) == 0x7D644
    assert function(0, 1, 1, 0, 1, 0) == 0x7D644
    assert function(0, 1, 1, 1, 0, 0) == 0x7D654
    assert function(0, 1, 1, 1, 1, 1) == 0x7D654

print("PASS: 0x7d4e8 state-4 selector-body vectors")
