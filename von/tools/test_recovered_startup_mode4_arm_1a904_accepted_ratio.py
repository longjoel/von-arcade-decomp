#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
names = (
    "retry_address retry_before retry_after retry_limit first_numerator_address first_numerator_raw "
    "first_denominator_address first_denominator_raw second_numerator_address second_numerator_raw "
    "second_denominator_address second_denominator_raw callback_register state_address state_value "
    "command_address command_value phase_address phase_value continuation ratio_less ratio_equal "
    "ratio_greater threshold_fallback invalid_denominator"
).split()

class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in names]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1a904-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1a904_accepted_ratio.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1a904_accepted_ratio
    fn.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0, 3, 1, 1, 2, 0x77, 0x1234, ctypes.byref(out))
    assert (out.retry_after, out.ratio_less, out.state_value, out.command_value, out.continuation) == (1, 1, 1, 0x41, 0x1ac44)
    fn(1, 1, 2, 1, 2, 0x77, 0x1234, ctypes.byref(out))
    assert (out.ratio_equal, out.state_value, out.command_value) == (1, 2, 0x42)
    fn(3, 1, 2, 3, 1, 0x77, 0x1234, ctypes.byref(out))
    assert (out.ratio_greater, out.state_value, out.command_value) == (1, 0x77, 0x40)
    fn(4, 1, 1, 1, 1, 0x77, 0x1234, ctypes.byref(out))
    assert (out.threshold_fallback, out.continuation) == (1, 0x1a9e0)
    fn(0, 0, 1, 1, 1, 0x77, 0x1234, ctypes.byref(out))
    assert out.invalid_denominator == 1
print("PASS: 0x1a904 slot-10 accepted ratio arm")
