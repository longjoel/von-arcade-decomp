#!/usr/bin/env python3
"""Check the post-status scheduler table at i960 0x82b4c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_dispatch_82b4c.c"


class Plan(ctypes.Structure):
    _fields_ = [("dispatched", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_dispatch_82b4c
    function.argtypes = [ctypes.c_uint32] * 3
    function.restype = Plan

    expected = [
        0x82D68, 0x82D68, 0x82D68, 0x82D68, 0x82D68, 0x82C54,
        0x82C08, 0x82C54, 0x82C18, 0x82C28, 0x82C38, 0x82C60,
        0x82D68, 0x82D68, 0x82D68, 0x82D68, 0x82D68, 0x82D68,
        0x82D68, 0x82C6C, 0x82CC0, 0x82CC8, 0x82CD0, 0x82CD8,
        0x82CE0, 0x82CC8, 0x82CB0, 0x82CE8, 0x82D04, 0x82D68,
        0x82D68, 0x82D68, 0x82D18, 0x82CC8, 0x82CC8, 0x82CC0,
        0x82CC0, 0x82CB0, 0x82D34, 0x82D48, 0x82D68, 0x82D68,
        0x82D68, 0x82D5C,
    ]
    for selector, target in enumerate(expected):
        result = function(1, 43, selector)
        assert (result.dispatched, result.target) == (1, target)
    assert function(0, 43, 0).dispatched == 0
    assert function(1, 42, 43).dispatched == 0
    assert function(1, 43, 44).dispatched == 0

print("recovered 0x82b4c scheduler-dispatch vectors: ok")
