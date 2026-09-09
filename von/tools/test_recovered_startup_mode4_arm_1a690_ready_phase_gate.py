#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "ready_address", "ready_value", "row_address", "row_value", "result_r5",
        "phase_address", "phase_value", "phase_mask", "phase_masked", "gate_entered",
        "phase_latch", "setup_call", "setup_call_count", "setup_argument", "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1a690-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1a690_ready_phase_gate.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1a690_ready_phase_gate
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Result)]
    out = Result()
    fn(1, 9, 3, 0, ctypes.byref(out))
    assert (out.gate_entered, out.continuation, out.setup_call_count) == (0, 0x1a7d0, 0)
    fn(0, 9, 0, 9, ctypes.byref(out))
    assert (out.phase_mask, out.phase_masked, out.phase_latch, out.setup_call_count, out.continuation) == (7, 1, 1, 0, 0x1a778)
    fn(0, 9, 2, 8, ctypes.byref(out))
    assert (out.phase_mask, out.phase_masked, out.phase_latch, out.setup_call_count) == (15, 8, 0, 0)
    fn(0, 9, 6, 0, ctypes.byref(out))
    assert (out.phase_mask, out.phase_masked, out.phase_latch, out.setup_call_count, out.setup_argument) == (63, 0, 1, 1, 0x1340)
print("PASS: 0x1a690 slot-10 ready/phase gate")
