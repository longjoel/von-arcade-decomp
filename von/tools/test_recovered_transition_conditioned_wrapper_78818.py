#!/usr/bin/env python3
"""Check the conditioned transition adapter recovered at 0x78818."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_conditioned_wrapper_78818.c"


class State(ctypes.Structure):
    _fields_ = [
        ("transition", ctypes.c_uint32),
        ("action", ctypes.c_uint32),
        ("status", ctypes.c_uint32),
        ("selector_state", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-conditioned.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_conditioned_wrapper_78818
    function.argtypes = [
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(State),
    ]
    function.restype = None
    function_d50 = api.recovered_transition_conditioned_wrapper_78d50
    function_d50.argtypes = function.argtypes
    function_d50.restype = None
    table = (ctypes.c_uint32 * 4)(8, 12, 13, 19)
    state = State()

    function(table, 2, 0, 1, ctypes.byref(state))
    assert (state.transition, state.action, state.status,
            state.selector_state) == (13, 5, 0, 0)

    function(table, 1, 1 << 5, 0, ctypes.byref(state))
    assert (state.transition, state.action, state.status,
            state.selector_state) == (12, 5, 0, 0)

    function(table, 3, 1 << 5, 1, ctypes.byref(state))
    assert (state.transition, state.action, state.status,
            state.selector_state) == (19, 20, 1, 6)

    function_d50(table, 0, 0, 1, ctypes.byref(state))
    assert (state.transition, state.action, state.status,
            state.selector_state) == (8, 5, 0, 0)
    function_d50(table, 2, 1 << 5, 1, ctypes.byref(state))
    assert (state.transition, state.action, state.status,
            state.selector_state) == (13, 20, 1, 18)

print("recovered conditioned transition-wrapper vectors: ok")
