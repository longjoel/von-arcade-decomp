#!/usr/bin/env python3
"""Check the state-2 selector body at i960 0x7d3a4."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_selector_body_2_7d3a4.c"


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-selector-body-2.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_selector_body_2_7d3a4
    function.argtypes = [ctypes.c_uint32] * 3
    function.restype = ctypes.c_uint32

    assert function(2, 0, 1) == 0x7D5F4
    assert function(0, 0, 0) == 0x7D654
    assert function(0, 1, 0) == 0x7D644
    assert function(0, 1, 1) == 0x7D654

print("PASS: 0x7d3a4 state-2 selector-body vectors")
