#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "first_numerator_address", "first_numerator_raw", "first_denominator_address",
        "first_denominator_raw", "second_numerator_address", "second_numerator_raw",
        "second_denominator_address", "second_denominator_raw", "callback_register",
        "counter_address", "counter_before", "counter_after", "state_address", "state_value",
        "command_address", "command_value", "ratio_less", "ratio_equal", "ratio_greater",
        "invalid_denominator", "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1ab40-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1ab40_ratio_state_arm.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1ab40_ratio_state_arm
    fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Result)]
    out = Result()
    fn(3, 1, 1, 2, 0x77, 4, ctypes.byref(out))
    assert (out.ratio_less, out.state_value, out.command_value, out.counter_after) == (1, 1, 0x41, 4)
    fn(1, 2, 1, 2, 0x77, 4, ctypes.byref(out))
    assert (out.ratio_equal, out.state_value, out.command_value, out.counter_after) == (1, 2, 0x42, 4)
    fn(1, 2, 3, 1, 0x77, 0xffffffff, ctypes.byref(out))
    assert (out.ratio_greater, out.state_value, out.command_value, out.counter_after) == (1, 0x77, 0x40, 0)
    fn(0, 1, 1, 1, 0, 0, ctypes.byref(out))
    assert out.invalid_denominator == 1
print("PASS: 0x1ab40 slot-10 ratio state arm")
