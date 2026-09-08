#!/usr/bin/env python3
"""Check the state-5 selector body at i960 0x7d568."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_selector_body_5_7d568.c"


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-selector-body-5.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_selector_body_5_7d568
    function.argtypes = [ctypes.c_uint32] * 5
    function.restype = ctypes.c_uint32

    assert function(0, 1, 1, 1, 2) == 0x7D644
    assert function(1, 0, 0, 1, 2) == 0x7D644
    assert function(1, 1, 1, 0, 2) == 0x7D644
    assert function(1, 1, 1, 1, 0) == 0x7D644
    assert function(1, 1, 1, 1, 2) == 0x7D5F4

print("PASS: 0x7d568 state-5 selector-body vectors")
