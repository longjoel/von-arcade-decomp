#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_allocator_commit.c"
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "allocator-commit.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_geometry_allocator_commit
    function.argtypes = [
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
    ]
    for allocated in (0, 1, 31, 0xffffffff):
        for count in (0, 1, 63, 0xffffffff):
            link = ctypes.c_uint32()
            new_count = ctypes.c_uint32()
            head = ctypes.c_uint32()
            available = ctypes.c_uint32()
            function(allocated, count, 0x51c854, 0x100 + count,
                     ctypes.byref(link), ctypes.byref(new_count),
                     ctypes.byref(head), ctypes.byref(available))
            assert link.value == allocated
            assert new_count.value == (count + 1) & 0xffffffff
            assert head.value == 0x51c884
            assert available.value == (-(0x100 + count)) & 0xffffffff

print("recovered geometry allocator-commit vectors: ok")
