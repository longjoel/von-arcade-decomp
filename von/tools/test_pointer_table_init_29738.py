#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_pointer_table_init_29738.c"

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "pointer-table.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    fn = lib.recovered_pointer_table_init_29738
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
    for head, stride in ((0x5150C0, 0x40), (0x5190C0, 0x100)):
        links = (ctypes.c_uint32 * 64)(*[0xffffffff] * 64)
        fn(head, stride, links)
        assert links[0] == head + stride
        assert links[62] == head + 63 * stride
        assert links[63] == 0

print("PASS: original 0x29738/0x29778 pointer-table initialization")
