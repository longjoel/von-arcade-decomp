#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "ready_address", "ready_value", "base_address", "base_before", "base_after", "divisor",
        "register_r17", "register_r29", "base_value", "base_remainder", "base_quotient",
        "bucket_divisor", "bucket_quotient", "offset_value", "offset_remainder", "scaled_remainder",
        "grid_stride", "grid_index", "helper_address", "helper_call_count", "helper_argument0",
        "helper_argument1", "helper_argument2", "invalid_divisor", "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1a7d0-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1a7d0_grid_update.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1a7d0_grid_update
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Result)]
    out = Result()
    fn(1, 10, 9, 5, ctypes.byref(out))
    assert (out.base_after, out.helper_call_count, out.continuation) == (11, 0, 0x1a820)
    fn(0, 100, 9, 5, ctypes.byref(out))
    assert (out.base_value, out.divisor, out.base_remainder, out.base_quotient, out.bucket_quotient, out.offset_remainder, out.grid_stride, out.grid_index, out.helper_argument0, out.helper_argument1, out.helper_argument2) == (40, 101, 40, 0, 28, 0, 1400, 0, 0, 0, 0)
    fn(0, 99, 9, 5, ctypes.byref(out))
    assert (out.base_value, out.divisor, out.base_remainder, out.base_quotient, out.offset_remainder, out.grid_stride, out.grid_index, out.helper_call_count) == (40, 100, 40, 0, 0, 1400, 0, 0)
    fn(0, 10, 100, 5, ctypes.byref(out))
    assert (out.base_after, out.base_value, out.base_remainder, out.base_quotient, out.bucket_quotient, out.offset_remainder, out.grid_stride, out.grid_index, out.helper_argument0, out.helper_argument1, out.helper_argument2, out.helper_call_count) == (11, 131, 10, 11, 261, 3, 350, 0, 261, 3, 0, 1)
    fn(0, 0xffffffff, 0xffffffff, 5, ctypes.byref(out))
    assert out.invalid_divisor == 1
print("PASS: 0x1a7d0 slot-10 grid update")
