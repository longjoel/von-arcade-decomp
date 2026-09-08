#!/usr/bin/env python3
"""Check the timing/state selector at i960 0x81f60."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_timing_selector_81f60.c"


class Plan(ctypes.Structure):
    _fields_ = [("value_504d78", ctypes.c_uint32),
                ("state_504d7c", ctypes.c_uint32),
                ("clear_504d88", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtiming-selector.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_timing_selector_81f60
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32]
    function.restype = Plan

    result = function(9, 0xbf800000, 6, 1, 0, 0)
    assert (result.value_504d78, result.state_504d7c) == (3, 6)
    assert function(9, 0x00000000, 6, 0, 0, 0).value_504d78 == 1
    assert function(9, 0, 3, 0, 0, 0).value_504d78 == 0
    assert function(9, 0, 4, 0, 1, 200).clear_504d88 == 1
    assert function(9, 0, 4, 0, 1, 200).state_504d7c == 6
    assert function(9, 0, 4, 1, 0, 200).clear_504d88 == 0
    assert function(9, 0, 4, 1, 0, 200).value_504d78 == 3

print("recovered 0x81f60 timing-selector vectors: ok")
