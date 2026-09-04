#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory() as d:
    so = pathlib.Path(d) / "dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(so), str(ROOT / "von/i960/recovered_progress_dispatch_2ba44.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_progress_dispatch_2ba44
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]; fn.restype = ctypes.c_uint32
    assert fn(7, 0, 0) == 1 and fn(7, 2, 0xe3ab0) == 1
    assert fn(7, 1, 0xe3ab0) == 0 and fn(7, 2, 0x1234) == 0
print("PASS: original 0x2ba44 progress dispatch decision vectors")
