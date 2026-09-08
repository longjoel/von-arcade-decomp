#!/usr/bin/env python3
"""Validate the ABI-visible startup continuation thunk at 0x18918."""
import ctypes
import pathlib
import subprocess
import tempfile


class Thunk(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("continuation", "return_value", "g14_cleared")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "thunk.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_startup_return_thunk_18918.c"),
                    "-o", str(so)], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_return_thunk_18918
    fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Thunk)]
    for continuation in (0, 0x18928, 0xFFFFFFFF):
        out = Thunk()
        fn(continuation, ctypes.byref(out))
        actual = tuple(getattr(out, name) for name, _ in Thunk._fields_)
        if actual != (continuation, 0, 1):
            raise SystemExit("0x18918 continuation mismatch")

print("PASS: 0x18918 startup return thunk")
