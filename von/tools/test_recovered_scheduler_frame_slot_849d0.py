#!/usr/bin/env python3
"""Check frame-slot arithmetic at i960 0x849d0."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_frame_slot_849d0.c"

class Plan(ctypes.Structure):
    _fields_ = [("normalized_delay", ctypes.c_int32),
                ("slot", ctypes.c_int32),
                ("byte_offset", ctypes.c_int32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib849d0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_frame_slot_849d0
    function.argtypes = [ctypes.c_int32, ctypes.c_int32]
    function.restype = Plan
    assert (function(6, 20).normalized_delay,
            function(6, 20).slot, function(6, 20).byte_offset) == (5, 15, 240)
    assert (function(0, 20).normalized_delay,
            function(0, 20).slot) == (180, -100)
    assert function(181, 20).slot == -100

print("recovered 0x849d0 frame-slot vectors: ok")
