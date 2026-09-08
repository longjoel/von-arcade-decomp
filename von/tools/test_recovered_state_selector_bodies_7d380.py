#!/usr/bin/env python3
"""Check the first two state-selector bodies at i960 0x7d380."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_selector_bodies_7d380.c"


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-selector-bodies.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    body0 = api.recovered_state_selector_body_0_7d380
    body1 = api.recovered_state_selector_body_1_7d390
    body0.argtypes = body1.argtypes = [ctypes.c_uint32]
    body0.restype = body1.restype = ctypes.c_uint32

    assert body0(0) == 0x7D644
    assert body0(2) == 0x7D5F4
    assert body1(0) == 0x7D644
    assert body1(4) == 0x7D4B4
    assert body1(2) == 0x7D5F4
    assert body1(6) == 0x7D5F4

print("PASS: 0x7d380/0x7d390 selector-body vectors")
