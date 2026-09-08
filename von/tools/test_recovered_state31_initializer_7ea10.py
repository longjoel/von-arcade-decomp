#!/usr/bin/env python3
"""Check the state-31 and threshold dispatch at i960 0x7ea10."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_initializer_7ea10.c"


class Plan(ctypes.Structure):
    _fields_ = [("accepted", ctypes.c_uint32),
                ("special_state31", ctypes.c_uint32),
                ("threshold_address", ctypes.c_uint32),
                ("status_504d9c", ctypes.c_uint32),
                ("value_504da0", ctypes.c_uint32),
                ("status_504d94", ctypes.c_uint32),
                ("status_504d98", ctypes.c_uint32),
                ("value_504db8", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-initializer.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_initializer_7ea10
    function.argtypes = [ctypes.c_int32, ctypes.c_uint16,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint16)]
    function.restype = Plan
    thresholds = (ctypes.c_uint16 * 3)(10, 20, 30)

    result = function(0x1f4, 31, 6, 6, 3, 0, thresholds)
    assert (result.accepted, result.special_state31,
            result.status_504d9c, result.value_504da0,
            result.status_504d94, result.status_504d98,
            result.value_504db8) == (1, 1, 3, 100, 1, 7, 30)
    assert function(0x1f3, 31, 6, 6, 3, 0, thresholds).accepted == 0
    assert function(0x1f4, 31, 6, 5, 3, 0, thresholds).accepted == 0

    result = function(0x1f4, 9, 0, 0, 0, 3, thresholds)
    assert (result.accepted, result.threshold_address) == (1, 0x504e3e)
    assert function(0x1f4, 11, 0, 0, 0, 0, thresholds).accepted == 0
    assert function(0x1f4, 1, 0, 0, 0, 8, thresholds).accepted == 0

print("recovered 0x7ea10 state31-initializer vectors: ok")
