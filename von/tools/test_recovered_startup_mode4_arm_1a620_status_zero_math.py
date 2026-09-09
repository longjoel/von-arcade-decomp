#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "status_word", "phase_divisor", "register_r17", "register_r16",
        "status_nonzero_bypass", "invalid_divisor", "record_helper_address",
        "record_helper_call_count", "record_helper_argument0", "record_helper_argument1",
        "arithmetic_helper_address", "arithmetic_helper_call_count",
        "arithmetic_helper_argument0", "arithmetic_helper_argument1", "base_value",
        "base_remainder", "base_quotient", "derived_stride", "result_r5", "result_r6",
        "setup_call", "setup_call_count", "setup_argument", "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1a620-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1a620_status_zero_math.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1a620_status_zero_math
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Result)]
    out = Result()
    fn(1, 7, 4, 8, ctypes.byref(out))
    assert (out.status_nonzero_bypass, out.record_helper_call_count, out.continuation) == (1, 0, 0x1a7c8)
    fn(0, 8, 1, 8, ctypes.byref(out))
    assert (out.base_value, out.base_remainder, out.base_quotient, out.derived_stride, out.result_r5, out.result_r6, out.record_helper_call_count, out.arithmetic_helper_call_count, out.setup_call_count) == (32, 0, 4, 1365, 5, 0, 1, 1, 1)
    fn(0, 8, 7, 8, ctypes.byref(out))
    assert (out.base_value, out.base_remainder, out.result_r5, out.setup_call_count, out.setup_argument, out.continuation) == (38, 6, 5, 0, 0x1148, 0x1a690)
    fn(0, 0, 1, 8, ctypes.byref(out))
    assert out.invalid_divisor == 1
print("PASS: 0x1a620 slot-10 status-zero arithmetic")
