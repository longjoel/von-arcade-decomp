#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_object_state_tail.c"
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "state-tail.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)
    ], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_object_state_tail
    function.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    for tag in range(32):
        for current in range(8):
            for caller in range(8):
                for pending in range(16):
                    result = ctypes.c_uint32(pending)
                    changed = function(tag, current, caller, pending,
                                       ctypes.byref(result))
                    expected = {7: 10, 8: 11, 9: 12}.get(pending)
                    active = tag == 31 and current == 3 and caller == 6
                    assert bool(changed) == bool(active and expected is not None)
                    assert result.value == (expected if active and expected is not None else pending)

print("recovered object-state tail vectors: ok")
