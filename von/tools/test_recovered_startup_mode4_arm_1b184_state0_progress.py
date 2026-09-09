#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "ready_address", "ready_value", "marker_address", "marker_value", "marker_match",
        "mode_address", "mode_value", "mode_target", "stored_address", "stored_raw",
        "stored_signed", "stored_target", "stored_updated", "stored_update_value",
        "callback_address", "callback_value", "state_address", "state_value", "counter_address",
        "counter_before", "counter_after", "limit_address", "limit_value", "progress_address",
        "progress_before", "progress_after", "progress_triggered", "trigger_helper",
        "progress_helper", "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1b184-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1b184_state0_progress.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1b184_state0_progress
    fn.argtypes = [ctypes.c_uint32] * 8 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0, 9, 6, 5, 10, 20, 3, 0x77, ctypes.byref(out))
    assert (out.marker_match, out.stored_updated, out.stored_update_value, out.counter_after, out.state_value, out.progress_triggered, out.continuation) == (1, 1, 6, 11, 3, 0, 0x1b2fc)
    fn(0, 8, 0, 5, 10, 20, 3, 0x77, ctypes.byref(out))
    assert (out.stored_updated, out.stored_update_value) == (1, 36)
    fn(0, 8, 36, 5, 10, 20, 3, 0x77, ctypes.byref(out))
    assert out.stored_updated == 0
    fn(1, 8, 0, 5, 20, 20, 3, 0x77, ctypes.byref(out))
    assert (out.stored_updated, out.progress_triggered, out.progress_after) == (0, 1, 4)
    fn(1, 8, 0, 5, 19, 20, 3, 0x77, ctypes.byref(out))
    assert out.progress_triggered == 0
    fn(1, 8, 0, 5, 0x7fffffff, 0, 3, 0x77, ctypes.byref(out))
    assert out.counter_after == 0x80000000 and out.progress_triggered == 0
print("PASS: 0x1b184 slot-11 state-0 progress arm")
