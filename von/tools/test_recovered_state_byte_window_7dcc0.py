#!/usr/bin/env python3
"""Check the entry guard and byte-window predicate at i960 0x7dcc0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_byte_window_7dcc0.c"


class Plan(ctypes.Structure):
    _fields_ = [("entry_allowed", ctypes.c_uint32),
                ("byte_match", ctypes.c_uint32),
                ("status_masks", ctypes.c_uint32 * 2)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-byte-window.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_byte_window_7dcc0
    function.argtypes = [ctypes.c_int32, ctypes.c_uint8, ctypes.c_uint8,
                         ctypes.c_uint16]
    function.restype = Plan

    assert function(0x1f3, 10, 10, 0).entry_allowed == 0
    assert function(0x1f4, 10, 10, 0).byte_match == 1
    assert function(0x1f4, 10, 15, 0).byte_match == 1
    assert function(0x1f4, 10, 16, 0).byte_match == 0
    assert function(0x1f4, 0, 0, 0).byte_match == 0
    assert function(0x1f4, 10, 10, 0x0100).byte_match == 0

    masks = api.recovered_state_byte_window_masks_7dcc0
    masks.argtypes = [ctypes.POINTER(ctypes.c_uint8),
                      ctypes.POINTER(ctypes.c_uint8),
                      ctypes.POINTER(ctypes.c_uint16),
                      ctypes.POINTER(ctypes.c_uint32)]
    masks.restype = None
    statuses = (ctypes.c_uint8 * 2)(10, 20)
    objects = (ctypes.c_uint8 * 32)(*([0] * 32))
    halfwords = (ctypes.c_uint16 * 32)(*([0] * 32))
    objects[0], objects[1], objects[2] = 10, 15, 20
    halfwords[1] = 0x0100
    output = (ctypes.c_uint32 * 2)()
    masks(statuses, objects, halfwords, output)
    assert tuple(output) == (1 << 0, 1 << 2)

print("recovered 0x7dcc0 byte-window vectors: ok")
