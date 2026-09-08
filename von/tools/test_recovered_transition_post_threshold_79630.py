#!/usr/bin/env python3
"""Check the bounded post-threshold selector at 0x79630."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_post_threshold_79630.c"


class State(ctypes.Structure):
    _fields_ = [("transition", ctypes.c_uint32),
                ("table_selected", ctypes.c_uint32),
                ("reentered_shared_state", ctypes.c_uint32),
                ("action", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-post-threshold.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_post_threshold_79630
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(State)]
    function.restype = None
    state = State()
    expected = [1, 1, 2, 2, 3, 3, 5, 6]
    for index, transition in enumerate(expected):
        function(index, 0xaaaa0000 + index, ctypes.byref(state))
        assert (state.transition, state.table_selected,
                state.reentered_shared_state, state.action) == (transition, 1, 1, 30)
    for index in (8, 99, 0xffffffff):
        function(index, 0xdeadbeef, ctypes.byref(state))
        assert (state.transition, state.table_selected,
                state.reentered_shared_state, state.action) == (0xdeadbeef, 0, 1, 30)

print("recovered post-threshold selector vectors: ok")
