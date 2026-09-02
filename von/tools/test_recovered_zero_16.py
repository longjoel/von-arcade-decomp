#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_zero_16.c"

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "zero16.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_zero_16
    function.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
    values = (ctypes.c_uint8 * 20)(*[0xa5] * 20)
    function(ctypes.cast(ctypes.byref(values, 2), ctypes.POINTER(ctypes.c_uint8)))
    assert list(values[:2]) == [0xa5, 0xa5]
    assert list(values[2:18]) == [0] * 16
    assert list(values[18:]) == [0xa5, 0xa5]

print("recovered 16-byte clear vectors: ok")
