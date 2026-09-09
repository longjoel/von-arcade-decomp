#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "phase_address", "phase_before", "phase_after", "increment", "next_address")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1ac44-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1ac44_phase_advance.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1ac44_phase_advance
    fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
    out = Result()
    fn(9, ctypes.byref(out))
    assert (out.phase_address, out.phase_before, out.phase_after, out.increment, out.next_address) == (0x503a00, 9, 10, 1, 0x1ac50)
    fn(0xffffffff, ctypes.byref(out))
    assert out.phase_after == 0
print("PASS: 0x1ac44 slot-10 phase advance")
