#!/usr/bin/env python3
"""Check the literal state-handler table at i960 0x7d358."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_selector_table_7d358.c"


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-selector-table.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_selector_target_7d358
    function.argtypes = [ctypes.c_uint32]
    function.restype = ctypes.c_uint32

    expected = [
        0x7D380, 0x7D390, 0x7D3A4, 0x7D404, 0x7D4E8,
        0x7D568, 0x7D5A4, 0x7D5DC, 0x7D604, 0x7D660,
    ]
    for state, target in enumerate(expected):
        assert function(state) == target
    assert function(10) == 0
    assert function(0xFFFFFFFF) == 0

print("PASS: 0x7d358 state-selector table vectors")
