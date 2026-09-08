#!/usr/bin/env python3
"""Check success publication at i960 0x85058."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_success_publication_85058.c"

class Plan(ctypes.Structure):
    _fields_ = [("value_504e42", ctypes.c_uint32),
                ("value_504e44", ctypes.c_uint32),
                ("restores_g8", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib85058.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_success_publication_85058
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(0, 0x4567)
    assert (result.value_504e42, result.value_504e44, result.restores_g8) == (0x200, 0x4567, 1)
    assert function(0x55, 9).value_504e42 == 0x255

print("recovered 0x85058 success-publication vectors: ok")
