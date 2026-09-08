#!/usr/bin/env python3
"""Check the fixed-point ratio predicate at i960 0x850c0."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_ratio_predicate_850c0.c"


class Plan(ctypes.Structure):
    _fields_ = [("object_ratio", ctypes.c_float),
                ("related_ratio", ctypes.c_float),
                ("difference", ctypes.c_float),
                ("exits_to_85128", ctypes.c_uint32),
                ("continues_to_85134", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib850c0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_ratio_predicate_850c0
    function.argtypes = [ctypes.c_int16, ctypes.c_int16,
                         ctypes.c_int16, ctypes.c_int16]
    function.restype = Plan
    result = function(1, 2, 3, 4)
    assert result.object_ratio == ctypes.c_float(0.5).value
    assert result.related_ratio == ctypes.c_float(0.75).value
    assert (result.exits_to_85128, result.continues_to_85134) == (0, 1)
    result = function(3, 4, 1, 2)
    assert (result.exits_to_85128, result.continues_to_85134) == (1, 0)
    result = function(2, 1, 4, 2)
    assert (result.exits_to_85128, result.continues_to_85134) == (1, 0)
    # ldos plus the shift pair retains signed halfword values.
    result = function(-2, 1, 4, 1)
    assert (result.exits_to_85128, result.continues_to_85134) == (0, 1)

print("recovered 0x850c0 ratio-predicate vectors: ok")
