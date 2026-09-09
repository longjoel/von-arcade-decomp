#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in ("call_count",)]
    _fields_ += [("call_target", ctypes.c_uint32 * 2), ("continuation", ctypes.c_uint32)]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1b614-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1b614_completion_bridge.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1b614_completion_bridge
    fn.argtypes = [ctypes.POINTER(Result)]
    out = Result()
    fn(ctypes.byref(out))
    assert (out.call_count, list(out.call_target), out.continuation) == (2, [0x43ee8, 0x423a8], 0x1b61c)
print("PASS: 0x1b614 slot-12 completion bridge")
