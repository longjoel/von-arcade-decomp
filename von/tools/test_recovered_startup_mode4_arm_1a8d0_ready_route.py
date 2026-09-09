#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "ready_address", "ready_value", "hardware_address", "hardware_mode", "status_address",
        "status_word", "status_threshold", "result_r5", "result_r6", "accepted", "rejected",
        "ready_clear_target", "hardware_target", "failed_status_target", "accepted_target",
        "selected_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1a8d0-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1a8d0_ready_route.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1a8d0_ready_route
    fn.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0, 1, 0, 0, 0, ctypes.byref(out))
    assert out.selected_target == 0x1aad4
    fn(1, 1, 0, 0, 0, ctypes.byref(out))
    assert out.selected_target == 0x1aa20
    fn(1, 0, 0, 1, 0, ctypes.byref(out))
    assert (out.rejected, out.selected_target) == (1, 0x1a9e0)
    fn(1, 0, 0xf423f, 0, 0, ctypes.byref(out))
    assert out.selected_target == 0x1a9e0
    fn(1, 0, 0xf423e, 0, 0, ctypes.byref(out))
    assert (out.accepted, out.rejected, out.selected_target) == (1, 0, 0x1a904)
print("PASS: 0x1a8d0 slot-10 ready/status route")
