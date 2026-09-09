#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "mode_address", "mode_value", "mode_target", "latch_address", "latch_raw",
        "latch_signed", "latch_shifted", "latch_sentinel", "register_r10", "target_value",
        "latch_updated", "latch_update_value", "callback_address", "callback_value",
        "state_address", "state_value", "counter_address", "counter_before", "counter_after",
        "callback_save_address", "callback_save_value", "helper_call", "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1b244-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1b244_state45_latch.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1b244_state45_latch
    fn.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Result)]
    out = Result()
    fn(9, 6, 5, 10, 0x77, ctypes.byref(out))
    assert (out.latch_updated, out.latch_update_value, out.state_value, out.counter_after, out.helper_call, out.continuation) == (1, 6, 4, 11, 0x20180, 0x1b2fc)
    fn(8, 0, 5, 10, 0x77, ctypes.byref(out))
    assert (out.latch_updated, out.latch_update_value) == (1, 36)
    fn(8, 0x29, 5, 10, 0x77, ctypes.byref(out))
    assert (out.latch_shifted, out.latch_updated) == (0x290000, 0)
    fn(8, 0xffff, 5, 10, 0x77, ctypes.byref(out))
    assert (out.latch_signed, out.latch_updated, out.latch_update_value) == (0xffffffff, 1, 36)
print("PASS: 0x1b244 slot-11 state-4 latch arm")
