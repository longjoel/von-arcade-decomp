#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_template_copy_2b5b0.c"

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "template-copy.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    fn = lib.recovered_geometry_template_copy_2b5b0
    fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    for index in (0, 1, 7):
        source = (ctypes.c_uint32 * 21)(*[0x2aa80000 + i for i in range(21)])
        destination = (ctypes.c_uint32 * 21)(*[0xffffffff] * 21)
        address = fn(index, source, destination)
        assert address == 0x51c5b0 + index * 100
        assert list(destination) == list(source)

print("PASS: original 0x2b5b0 template-copy vectors (indices 0,1,7)")
