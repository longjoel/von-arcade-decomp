#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "ready_address", "ready_value", "base_address", "base_value", "divisor_value",
        "base_remainder", "base_quotient", "bucket_divisor", "bucket_quotient", "offset_value",
        "offset_remainder", "scaled_remainder", "helper_argument", "helper_call", "result_address",
        "continuation_call", "continuation_target", "valid")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1b470-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1b470_prefix.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1b470_prefix
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0, 1213, 9, 29, ctypes.byref(out))
    assert (out.divisor_value, out.base_remainder, out.base_quotient, out.scaled_remainder, out.helper_argument, out.valid, out.continuation_target) == (40, 13, 30, 13 * 99, (13 * 99) // 40, 1, 0x1b4b4)
    fn(1, 1213, 9, 29, ctypes.byref(out))
    assert (out.valid, out.base_remainder, out.helper_call) == (0, 0, 0)
    fn(0, 0, 0xffffffff, 29, ctypes.byref(out))
    assert out.valid == 0
print("PASS: 0x1b470 slot-12 setup prefix")
