#!/usr/bin/env python3
"""Check the status tail at i960 0x8168c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_status_tail_8168c.c"


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-status-tail.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_status_tail_8168c
    function.argtypes = [ctypes.c_int32, ctypes.c_uint32]
    function.restype = ctypes.c_uint32

    for value in (0, 119, 120, 239, 240, 359, 0xffffffff):
        expected = 18 if value % 240 <= 119 else 19
        assert function(0, value) == expected
        assert function(2, value) == 18
        assert function(7, value) == 18

print("recovered 0x8168c status-tail vectors: ok")
