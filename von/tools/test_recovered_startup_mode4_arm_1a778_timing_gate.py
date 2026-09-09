#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "status_address", "status_word", "phase_address", "phase_value", "workspace_address",
        "workspace_value", "timing_expression", "signed_negative", "low_three_bits",
        "aligned_negative", "helper_address", "helper_call_count", "helper_argument0",
        "helper_argument1", "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1a778-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1a778_timing_gate.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1a778_timing_gate
    fn.argtypes = [ctypes.c_uint32] * 2 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0, 0, ctypes.byref(out))
    assert (out.workspace_value, out.signed_negative, out.helper_call_count) == (0xf030, 0, 0)
    fn(0x200, 0, ctypes.byref(out))
    assert (out.workspace_value, out.signed_negative, out.low_three_bits, out.aligned_negative, out.helper_call_count) == (0x9030, 0, 0, 0, 0)
    fn(0x400, 0, ctypes.byref(out))
    assert (out.workspace_value, out.signed_negative, out.low_three_bits, out.aligned_negative, out.helper_call_count) == (0x3030, 0, 0, 0, 0)
    fn(0x800, 0, ctypes.byref(out))
    assert (out.workspace_value, out.signed_negative, out.low_three_bits, out.aligned_negative, out.helper_call_count) == (0xffff7030, 1, 0, 1, 1)
    assert (out.helper_argument0, out.helper_argument1, out.continuation) == (0xffffe33d, 1, 0x1a7d0)
print("PASS: 0x1a778 slot-10 timing gate")
