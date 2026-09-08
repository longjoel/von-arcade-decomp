#!/usr/bin/env python3
"""Check shared service postprocessing at i960 0x830c0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_service_postprocess_830c0.c"


class Plan(ctypes.Structure):
    _fields_ = [("value_504d94", ctypes.c_uint32),
                ("value_504d98", ctypes.c_uint32),
                ("value_504db8", ctypes.c_uint32),
                ("wrote_status_12", ctypes.c_uint32),
                ("wrote_related_default", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-service-postprocess.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_service_postprocess_830c0
    function.argtypes = [ctypes.c_uint32] * 4
    function.restype = Plan

    result = function(3, 9, 4, 77)
    assert (result.value_504d98, result.wrote_status_12,
            result.wrote_related_default) == (12, 1, 0)
    result = function(3, 9, 0, 77)
    assert (result.value_504d98, result.value_504db8,
            result.wrote_status_12, result.wrote_related_default) == (1, 10, 1, 1)
    result = function(2, 9, 0, 77)
    assert (result.value_504d98, result.value_504db8,
            result.wrote_status_12) == (1, 10, 0)
    assert function(2, 8, 4, 77).value_504d98 == 8

print("recovered 0x830c0 service-postprocess vectors: ok")
