#!/usr/bin/env python3
"""Check the early status prefix at i960 0x82650."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_status_prefix_82650.c"


class Plan(ctypes.Structure):
    _fields_ = [("terminal", ctypes.c_uint32),
                ("status_504d80", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-status-prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_status_prefix_82650
    function.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    function.restype = Plan

    assert (function(0, 0, 0).terminal,
            function(0, 0, 0).status_504d80) == (1, 8)
    assert function(0, 1, 4).status_504d80 == 3
    assert function(0, 1, 5).status_504d80 == 4
    assert function(1, 0, 0).terminal == 0
    assert function(0, 2, 0).terminal == 0

print("recovered 0x82650 status-prefix vectors: ok")
