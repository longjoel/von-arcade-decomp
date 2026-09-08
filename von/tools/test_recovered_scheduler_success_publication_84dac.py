#!/usr/bin/env python3
"""Check success publication at i960 0x84dac."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_success_publication_84dac.c"

class Plan(ctypes.Structure):
    _fields_ = [("value_504e42", ctypes.c_uint32),
                ("value_504e44", ctypes.c_uint32),
                ("continues_to_84f10", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84dac.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_success_publication_84dac
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(0, 0x1234)
    assert (result.value_504e42, result.value_504e44,
            result.continues_to_84f10) == (0x100, 0x1234, 1)
    assert function(0x55, 0).value_504e42 == 0x155

print("recovered 0x84dac success-publication vectors: ok")
