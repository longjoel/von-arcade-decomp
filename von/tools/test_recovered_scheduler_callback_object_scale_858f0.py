#!/usr/bin/env python3
"""Check callback object scaling at i960 0x858f0."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_callback_object_scale_858f0.c"

class Plan(ctypes.Structure):
    _fields_ = [("object_48", ctypes.c_int32),
                ("object_4a", ctypes.c_int32),
                ("object_190", ctypes.c_int32),
                ("related_state", ctypes.c_int32),
                ("related_source", ctypes.c_int32),
                ("normalized_48", ctypes.c_int32),
                ("normalized_4a", ctypes.c_int32),
                ("quotient", ctypes.c_int32),
                ("value_509b8c", ctypes.c_int32),
                ("value_509b90", ctypes.c_int32),
                ("scaled", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib858f0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_callback_object_scale_858f0
    function.argtypes = [ctypes.c_int16, ctypes.c_int16, ctypes.c_int32,
                         ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    function.restype = Plan
    result = function(-2, 6, 0, 11, 350, 999)
    assert (result.related_source, result.normalized_48,
            result.quotient, result.value_509b8c,
            result.value_509b90, result.scaled) == (63, -2, 3, -2, 18, 1)
    result = function(4, 7, 0, 14, 0, 450)
    assert (result.related_source, result.quotient, result.value_509b90,
            result.scaled) == (64, 4, 28, 1)
    result = function(4, 7, 1, 11, 350, 450)
    assert (result.related_source, result.value_509b90, result.scaled) == (0, 7, 0)
    assert function(4, 7, 0, 3, 350, 450).value_509b90 == 7

print("recovered 0x858f0 object-scale vectors: ok")
