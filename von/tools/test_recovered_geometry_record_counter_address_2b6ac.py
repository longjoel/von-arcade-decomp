#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory() as d:
    so = pathlib.Path(d) / "address.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(so), str(ROOT / "von/i960/recovered_geometry_record_counter_address_2b6ac.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_geometry_record_counter_address_2b6ac
    fn.argtypes = [ctypes.c_uint32]; fn.restype = ctypes.c_uint32
    for index in (0, 1, 7):
        assert fn(index) == 0x51c5b4 + index * 100
print("PASS: original 0x2b6ac record-counter address vectors")
