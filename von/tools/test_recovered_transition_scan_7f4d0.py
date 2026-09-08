#!/usr/bin/env python3
"""Check the two-byte 32-slot scan at i960 0x7f4d0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_scan_7f4d0.c"


class Plan(ctypes.Structure):
    _fields_ = [("entry_allowed", ctypes.c_uint32),
                ("status0_match_mask", ctypes.c_uint32),
                ("status1_match_mask", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-scan.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_scan_7f4d0
    function.argtypes = [ctypes.c_int32, ctypes.c_uint8, ctypes.c_uint8,
                         ctypes.POINTER(ctypes.c_uint8)]
    function.restype = Plan

    objects = (ctypes.c_uint8 * 32)(*([0] * 32))
    assert function(0x1f3, 10, 20, objects).entry_allowed == 0
    objects[0], objects[1], objects[31] = 10, 25, 24
    result = function(0x1f4, 10, 20, objects)
    assert result.entry_allowed == 1
    assert result.status0_match_mask == 1
    assert result.status1_match_mask == (1 << 1) | (1 << 31)
    objects[2] = 9
    assert function(0x1f4, 0, 9, objects).status0_match_mask == 0
    assert function(0x1f4, 0, 9, objects).status1_match_mask & (1 << 2)

print("recovered 0x7f4d0 transition-scan vectors: ok")
