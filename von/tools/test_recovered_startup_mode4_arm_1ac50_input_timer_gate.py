#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "threshold_address", "threshold_raw", "threshold_signed", "timer_address", "timer_raw",
        "timer_signed", "shifted_threshold", "timer_nonpositive", "timer_reaches_threshold",
        "controller_address", "controller_word", "controller_low_six", "controller_gate_open",
        "setup_helper", "setup_call_count", "setup_argument", "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1ac50-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1ac50_input_timer_gate.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1ac50_input_timer_gate
    fn.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Result)]
    out = Result()
    fn(80, 5, 0, ctypes.byref(out))
    assert (out.shifted_threshold, out.timer_nonpositive, out.timer_reaches_threshold, out.controller_gate_open, out.setup_call_count, out.setup_argument, out.continuation) == (10, 0, 0, 1, 1, 0x1110, 0x1ac8c)
    fn(80, 5, 1, ctypes.byref(out))
    assert (out.controller_low_six, out.setup_call_count) == (1, 0)
    fn(80, 10, 0, ctypes.byref(out))
    assert (out.timer_reaches_threshold, out.setup_call_count) == (1, 0)
    fn(80, 0, 0, ctypes.byref(out))
    assert (out.timer_nonpositive, out.setup_call_count) == (1, 0)
    fn(80, 0xffff, 0, ctypes.byref(out))
    assert (out.timer_signed, out.timer_nonpositive, out.timer_reaches_threshold, out.setup_call_count) == (0xffffffff, 1, 0, 0)
    fn(0xffff, 5, 0, ctypes.byref(out))
    assert (out.shifted_threshold, out.timer_reaches_threshold, out.setup_call_count) == (0x1fffffff, 0, 1)
print("PASS: 0x1ac50 slot-10 input/timer gate")
