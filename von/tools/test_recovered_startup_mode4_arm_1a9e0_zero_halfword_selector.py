#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "first_address", "first_raw", "first_zero", "second_address", "second_raw", "second_zero",
        "callback_register", "state_address", "state_value", "command_address", "command_value",
        "phase_address", "phase_before", "phase_after", "selected", "common_service_selected",
        "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1a9e0-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1a9e0_zero_halfword_selector.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1a9e0_zero_halfword_selector
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0, 7, 0x77, 9, ctypes.byref(out))
    assert (out.selected, out.state_value, out.command_value, out.phase_after, out.continuation) == (1, 1, 0x41, 10, 0x1ac44)
    fn(7, 0, 0x77, 9, ctypes.byref(out))
    assert (out.selected, out.state_value, out.command_value, out.phase_after, out.continuation) == (1, 0x77, 0x40, 10, 0x1ac44)
    fn(7, 9, 0x77, 9, ctypes.byref(out))
    assert (out.selected, out.common_service_selected, out.phase_after, out.continuation) == (0, 1, 9, 0x1ac50)
print("PASS: 0x1a9e0 slot-10 zero-halfword selector")
