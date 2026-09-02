#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_command_profile_dispatch.c"

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "profile-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    Callback = ctypes.CFUNCTYPE(None, ctypes.c_uint32)
    events = []
    prepare = Callback(lambda value: events.append(("prepare", value)))
    selected = Callback(lambda value: events.append(("selected", value)))
    handlers = (Callback * 24)()
    handlers[7] = selected
    function = lib.recovered_command_profile_dispatch
    function.argtypes = [
        ctypes.c_uint16, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32), Callback,
        ctypes.POINTER(Callback),
    ]
    selector = ctypes.c_uint32()
    assert function(0xe000, 2, 0x12345678, ctypes.byref(selector), prepare,
                    handlers) == 7
    assert selector.value == 7
    assert events == [("prepare", 0x12345678), ("selected", 0x12345678)]

    advance = lib.recovered_command_profile_advance
    advance.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                        ctypes.POINTER(Callback)]
    advance.restype = ctypes.c_uint32
    handlers[8] = Callback(lambda value: events.append(("advance", value)))
    input_value = ctypes.c_uint32(41)
    assert advance(2, ctypes.byref(input_value), handlers) == 8
    assert input_value.value == 42
    assert events[-1] == ("advance", 41)

print("recovered command-profile dispatch vectors: ok")
