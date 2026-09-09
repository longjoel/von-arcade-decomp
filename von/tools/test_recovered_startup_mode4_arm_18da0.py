#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "record_state_call", "record_state_first", "record_state_second",
        "formatter_call", "formatter_argument", "formatter_call_count",
        "progress_address", "progress_before", "progress_after",
        "counter_address", "counter_before", "counter_after", "divisor",
        "device_word_address", "device_word", "check_mask", "checks_required",
        "checks_passed", "status_a4", "status_a5", "status_a6", "status_gate",
        "extended_status_gate", "setup_call", "setup_argument", "setup_performed",
        "ready_address", "ready_before", "ready_after", "command_address",
        "command_value", "secondary_command_value", "phase_address", "phase_before",
        "phase_after", "progress_limit_reached", "counter_path", "fallback_path",
        "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-18da0-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_18da0.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_18da0
    fn.argtypes = [ctypes.c_uint32] * 10 + [ctypes.POINTER(Result)]
    out = Result()
    fn(4, 0, 5, 0, 0x7f, 0x10, 0, 0, 0, 2, ctypes.byref(out))
    assert (out.progress_after, out.status_gate, out.setup_call, out.setup_argument, out.counter_after, out.command_value, out.secondary_command_value, out.return_target) == (4, 1, 0x2a4e0, 0x1111, 1, 0x71, 0xffffffff, 0x18fa4)
    fn(4, 0, 0, 16, 0x7f, 0, 0, 0, 1, 2, ctypes.byref(out))
    assert (out.fallback_path, out.ready_after, out.counter_after, out.return_target) == (1, 0, 1, 0x18fa4)
    fn(0, 40, 9, 0, 0x7f, 0, 0, 0, 0, 2, ctypes.byref(out))
    assert (out.counter_path, out.counter_after, out.command_value, out.secondary_command_value, out.progress_after, out.phase_after, out.return_target) == (1, 41, 33, 0xffffffff, 0, 3, 0x1900c)
print("PASS: 0x18da0 startup phase-table arm")
