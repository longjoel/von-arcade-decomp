#!/usr/bin/env python3
"""Check the four-window range classifier at i960 0x7d930."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_range_class_7d930.c"


class Plan(ctypes.Structure):
    _fields_ = [("values", ctypes.c_uint32 * 4),
                ("threshold", ctypes.c_uint32),
                ("selected_class", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-range.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_range_class_7d930
    function.argtypes = [ctypes.c_int16]
    function.restype = Plan

    result = function(0)
    assert list(result.values) == [0xE24F, 0xA24F, 0x224F, 0x624F]
    assert (result.threshold, result.selected_class) == (0x49E, 0)
    result = function(0x10000 - 0xE24F)
    assert result.values[0] == 0
    assert result.selected_class == 1
    result = function(0x10000 - 0xE24F - 0x224F)
    assert result.values[0] == ((0x10000 - 0x224F) & 0xffff)
    assert result.selected_class == 0
    result = function(-1)
    assert list(result.values) == [0xE24E, 0xA24E, 0x224E, 0x624E]
    assert result.selected_class == 0

print("PASS: 0x7d930 range-class vectors")
