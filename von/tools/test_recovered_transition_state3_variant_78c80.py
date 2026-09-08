#!/usr/bin/env python3
"""Check the transition variant recovered at 0x78c80."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_state3_variant_78c80.c"


class State(ctypes.Structure):
    _fields_ = [("transition", ctypes.c_uint32), ("action", ctypes.c_uint32),
                ("status", ctypes.c_uint32), ("selector_state", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-state3-variant.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_state3_variant_78c80
    function.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(State)]
    table = (ctypes.c_uint32 * 4)(8, 12, 13, 19)
    state = State()

    function(table, 0, 2, 0, 1, ctypes.byref(state))
    assert (state.transition, state.action, state.status, state.selector_state) == (8, 5, 0, 0)
    function(table, 1, 3, 0xc, 1, ctypes.byref(state))
    assert (state.transition, state.action, state.status, state.selector_state) == (12, 20, 1, 18)
    function(table, 2, 2, 0x10, 1, ctypes.byref(state))
    assert (state.transition, state.action, state.status, state.selector_state) == (13, 20, 1, 17)
    function(table, 3, 3, 0x14, 1, ctypes.byref(state))
    assert (state.transition, state.action, state.status, state.selector_state) == (19, 20, 1, 18)
    function(table, 3, 3, 0x10, 0, ctypes.byref(state))
    assert (state.transition, state.action, state.status, state.selector_state) == (19, 5, 0, 0)

print("recovered state-3 variant transition-wrapper vectors: ok")
