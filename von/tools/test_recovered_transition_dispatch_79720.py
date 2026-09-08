#!/usr/bin/env python3
"""Check the post-threshold dispatch body at 0x79720."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_dispatch_79720.c"


class State(ctypes.Structure):
    _fields_ = [("transition", ctypes.c_uint32), ("action", ctypes.c_uint32),
                ("status", ctypes.c_uint32), ("reentered_shared_state", ctypes.c_uint32),
                ("entered_table", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_dispatch_79720
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(State)]
    state = State(0xabcdef01, 99, 7, 0, 0)

    function(0, 2, 1, ctypes.byref(state))
    assert (state.transition, state.action, state.status,
            state.reentered_shared_state, state.entered_table) == (0xabcdef01, 99, 7, 0, 0)
    function(1, 0, 0, ctypes.byref(state))
    assert (state.transition, state.action, state.status, state.reentered_shared_state, state.entered_table) == (18, 5, 7, 0, 1)
    function(1, 3, 0, ctypes.byref(state))
    assert (state.transition, state.action) == (12, 5)
    function(1, 6, 0, ctypes.byref(state))
    assert (state.transition, state.action) == (13, 5)
    function(1, 8, 0, ctypes.byref(state))
    assert (state.transition, state.action) == (19, 5)
    function(1, 9, 1, ctypes.byref(state))
    assert (state.transition, state.action, state.status,
            state.reentered_shared_state) == (1, 30, 1, 1)
    function(1, 10, 1, ctypes.byref(state))
    assert (state.transition, state.action, state.status,
            state.reentered_shared_state) == (1, 5, 1, 0)

print("recovered 0x79720 dispatch vectors: ok")
