#!/usr/bin/env python3
"""Check the shared service dispatch at i960 0x82fac."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_service_shared_dispatch_82fac.c"


class Plan(ctypes.Structure):
    _fields_ = [("dispatched", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-service-shared-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_service_shared_dispatch_82fac
    function.argtypes = [ctypes.c_uint32]
    function.restype = Plan

    expected = [0x82FDC, 0x82FF4, 0x8300C, 0x83024,
                0x8303C, 0x83050, 0x83058, 0x8307C]
    for selector, target in enumerate(expected):
        result = function(selector)
        assert (result.dispatched, result.target) == (1, target)
    assert function(8).dispatched == 0
    assert function(0xFFFFFFFF).dispatched == 0

print("recovered 0x82fac shared-dispatch vectors: ok")
