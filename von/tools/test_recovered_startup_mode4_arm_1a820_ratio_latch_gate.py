#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "numerator_address", "numerator_raw", "numerator_signed", "denominator_address",
        "denominator_raw", "denominator_signed", "alternate_numerator_address",
        "alternate_numerator_raw", "alternate_denominator_address", "alternate_denominator_raw",
        "hardware_mode_address", "hardware_mode", "latch_address", "latch_before", "latch_after",
        "ratio_less", "ratio_equal_or_greater", "invalid_denominator", "warning_service",
        "warning_call_count", "warning_code", "register_r14", "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1a820-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1a820_ratio_latch_gate.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1a820_ratio_latch_gate
    fn.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Result)]
    out = Result()
    fn(3, 1, 1, 2, 0, 0, 0x55, ctypes.byref(out))
    assert (out.ratio_less, out.warning_call_count, out.warning_code, out.latch_after, out.continuation) == (1, 1, 0x97, 1, 0x1a8d0)
    fn(3, 1, 1, 2, 1, 0, 0x55, ctypes.byref(out))
    assert (out.warning_call_count, out.warning_code, out.latch_after) == (1, 0x9f, 1)
    fn(1, 2, 1, 2, 0, 0, 0x55, ctypes.byref(out))
    assert (out.ratio_equal_or_greater, out.warning_code, out.latch_after) == (1, 0x91, 0x55)
    fn(1, 2, 1, 2, 1, 7, 0x55, ctypes.byref(out))
    assert (out.warning_call_count, out.latch_after) == (0, 7)
    fn(1, 0, 1, 2, 0, 0, 0, ctypes.byref(out))
    assert out.invalid_denominator == 1
print("PASS: 0x1a820 slot-10 ratio/latch gate")
