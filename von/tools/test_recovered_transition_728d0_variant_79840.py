#!/usr/bin/env python3
"""Check the post-threshold 0x728d0 variant at 0x79840."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_728d0_variant_79840.c"


class State(ctypes.Structure):
    _fields_ = [("transition", ctypes.c_uint32), ("action", ctypes.c_uint32),
                ("status", ctypes.c_uint32), ("reentered_shared_state", ctypes.c_uint32),
                ("entered_table", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-728d0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_728d0_variant_79840
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.POINTER(State)]
    state = State(0xabcdef01, 99, 7, 0, 0)

    function(0, 0, 44, 1, ctypes.byref(state))
    assert (state.transition, state.action, state.entered_table) == (0xabcdef01, 99, 0)
    function(1, 0, 44, 0, ctypes.byref(state))
    assert (state.transition, state.action) == (18, 5)
    function(1, 2, 44, 0, ctypes.byref(state))
    assert (state.transition, state.action) == (44, 5)
    function(1, 8, 44, 0, ctypes.byref(state))
    assert (state.transition, state.action) == (19, 5)
    function(1, 1, 44, 1, ctypes.byref(state))
    assert (state.transition, state.action, state.status,
            state.reentered_shared_state) == (1, 30, 1, 1)
    function(1, 8, 44, 1, ctypes.byref(state))
    assert (state.transition, state.action, state.status,
            state.reentered_shared_state) == (3, 30, 1, 1)

print("recovered 0x79840 0x728d0 variant vectors: ok")
