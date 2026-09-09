#!/usr/bin/env python3
"""Check shared service handler prefixes at i960 0x82fdc-0x830bc."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_service_shared_handler_prefix_82fdc.c"


class Plan(ctypes.Structure):
    _fields_ = [("write_504d94", ctypes.c_uint32),
                ("value_504d94", ctypes.c_uint32),
                ("write_504d98", ctypes.c_uint32),
                ("value_504d98", ctypes.c_uint32),
                ("write_504db8", ctypes.c_uint32),
                ("value_504db8", ctypes.c_uint32),
                ("calls_79050", ctypes.c_uint32),
                ("calls_79d60", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-service-handler-prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_service_shared_handler_prefix_82fdc
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    expected = {0: (5, 0, 30, 1, 0), 1: (6, 0, 30, 1, 0),
                2: (2, 0, 30, 1, 0), 3: (3, 0, 30, 1, 0),
                4: (99, 1, 10, 0, 0), 5: (99, 2, 20, 0, 0),
                6: (99, 3, 20, 0, 0), 7: (7, 0, 30, 0, 1)}
    for selector, (d94, d98, db8, call79050, call79d60) in expected.items():
        result = function(selector, 99)
        assert (result.value_504d94, result.value_504d98,
                result.value_504db8, result.calls_79050,
                result.calls_79d60) == (d94, d98, db8, call79050, call79d60)
    result = function(8, 99)
    assert (result.value_504d94, result.value_504d98,
            result.value_504db8) == (99, 1, 10)
    assert result.calls_79050 == 0

print("recovered 0x82fdc shared-handler-prefix vectors: ok")
