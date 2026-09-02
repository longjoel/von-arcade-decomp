#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_secondary_transition.c"
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "secondary-transition.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_secondary_transition_select
    function.restype = ctypes.c_uint32
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
    for gate in range(4):
        for state in range(16):
            transition = ctypes.c_uint32(0xabcdef01)
            changed = function(gate, state, ctypes.byref(transition))
            assert bool(changed) == (gate == 1)
            if gate == 1:
                assert transition.value == (2 if state == 7 else 1)
            else:
                assert transition.value == 0xabcdef01

print("recovered secondary-transition vectors: ok")
