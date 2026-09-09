#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "mode_address", "mode_before", "mode_after", "phase_address", "phase_before",
        "phase_after", "return_thunk", "branch_target", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-mode-8-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode_handler_8_18620.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode_handler_8_18620
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result)]
    out = Result()
    fn(15, 7, ctypes.byref(out))
    assert (out.mode_address, out.mode_before, out.mode_after, out.phase_address, out.phase_before, out.phase_after, out.return_thunk, out.branch_target, out.return_target) == (0x5039f4, 15, 0, 0x503a00, 7, 0, 0x18644, 0x18644, 0x18644)
    fn(0xffffffff, 0xffffffff, ctypes.byref(out))
    assert (out.mode_after, out.phase_after) == (0, 0)
print("PASS: 0x18620 startup mode handlers 8/15")
