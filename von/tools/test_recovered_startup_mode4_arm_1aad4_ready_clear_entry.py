#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "status_address", "status_word", "status_threshold", "result_r5", "result_r6",
        "phase_address", "phase_before", "phase_after", "admitted", "rejected", "zero_phase",
        "progress_helper", "progress_helper_call_count", "setup_helper", "setup_call_count",
        "setup_argument", "state_address", "state_value", "command_address", "command_value",
        "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1aad4-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1aad4_ready_clear_entry.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1aad4_ready_clear_entry
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0, 0, 0, 0, ctypes.byref(out))
    assert (out.admitted, out.zero_phase, out.phase_after, out.progress_helper_call_count, out.setup_call_count, out.setup_argument, out.state_value, out.command_value, out.continuation) == (1, 1, 1, 1, 1, 0x1012, 5, 0x43, 0x1ac50)
    fn(0, 0, 0, 4, ctypes.byref(out))
    assert (out.admitted, out.zero_phase, out.phase_after, out.progress_helper_call_count, out.continuation) == (1, 0, 5, 0, 0x1ab40)
    fn(0, 1, 0, 0, ctypes.byref(out))
    assert (out.rejected, out.continuation) == (1, 0x1abec)
    fn(0xf423f, 0, 0, 0, ctypes.byref(out))
    assert out.rejected == 1
print("PASS: 0x1aad4 slot-10 ready-clear entry")
