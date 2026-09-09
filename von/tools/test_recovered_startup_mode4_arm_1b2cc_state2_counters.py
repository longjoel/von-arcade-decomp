#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "counter_6c_address", "counter_6c_before", "counter_6c_after",
        "counter_70_address", "counter_70_before", "counter_70_after",
        "callback_address", "callback_value", "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1b2cc-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1b2cc_state2_counters.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1b2cc_state2_counters
    fn.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Result)]
    out = Result()
    fn(4, 9, 0x77, ctypes.byref(out))
    assert (out.counter_6c_after, out.counter_70_after, out.callback_address, out.callback_value, out.continuation) == (5, 10, 0x504b94, 0x77, 0x1b2fc)
    fn(0xffffffff, 0xffffffff, 0, ctypes.byref(out))
    assert (out.counter_6c_after, out.counter_70_after) == (0, 0)
print("PASS: 0x1b2cc slot-11 state-2 counters")
