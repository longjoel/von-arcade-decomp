#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory() as d:
    so = pathlib.Path(d) / "counter.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(so), str(ROOT / "von/i960/recovered_status_counter_add2_2b7b0.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_status_counter_add2_2b7b0
    fn.argtypes = [ctypes.c_uint32]; fn.restype = ctypes.c_uint32
    for value in (0, 1, 0x503a00, 0xffffffff):
        assert fn(value) == (value + 2) & 0xffffffff
print("PASS: original 0x2b7b0 status-counter add-2 vectors")
