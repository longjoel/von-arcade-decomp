#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_command_profile_initialize.c"

class State(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "callback_sentinel", "selector", "pending", "profile_long_low",
        "profile_long_high", "profile_word", "input_handle",
        "published_handle")]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "profile-init.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    Setup = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_uint32)
    Callback = ctypes.CFUNCTYPE(None, ctypes.c_uint32)
    events = []
    setup = Setup(lambda value: events.append(("setup", value)) or 0x1234)
    first = Callback(lambda value: events.append(("first", value)))
    initialize = Callback(lambda value: events.append(("initialize", value)))
    format_callback = Callback(lambda value: events.append(("format", value)))
    function = lib.recovered_command_profile_initialize
    function.argtypes = [
        ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        Setup, Callback, Callback, Callback, ctypes.POINTER(State),
    ]
    configurations = (ctypes.c_uint32 * 14)(*[100 + i for i in range(14)])
    low = (ctypes.c_uint32 * 14)(*[200 + i for i in range(14)])
    high = (ctypes.c_uint32 * 14)(*[300 + i for i in range(14)])
    words = (ctypes.c_uint32 * 14)(*[400 + i for i in range(14)])
    formats = (ctypes.c_uint32 * 14)(*[500 + i for i in range(14)])
    state = State(*([0xa5a5a5a5] * 8))
    function(2, configurations, low, high, words, formats, setup, first,
             initialize, format_callback, ctypes.byref(state))
    assert events == [("setup", 102), ("first", 2), ("initialize", 2),
                      ("format", 502)]
    assert state.callback_sentinel == 0xffffffff
    assert (state.selector, state.pending) == (0, 0)
    assert (state.profile_long_low, state.profile_long_high, state.profile_word) == (202, 302, 402)
    assert (state.input_handle, state.published_handle) == (0x1234, 0x1234)

    events.clear()
    function(13, configurations, low, high, words, formats, setup, first,
             initialize, format_callback, ctypes.byref(state))
    assert events == [("first", 13), ("initialize", 13), ("format", 513)]
    assert (state.input_handle, state.published_handle) == (0, 0)

print("recovered command-profile initializer vectors: ok")
