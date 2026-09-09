#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in ("ready_address", "ready_value", "record_pointer", "callback_target_a", "callback_target_b", "call_count", "conditional_call_included")]
    _fields_ += [("call_target", ctypes.c_uint32 * 17), ("call_argument", ctypes.c_uint32 * 17), ("continuation", ctypes.c_uint32)]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1ada0-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1ada0_common_service_plan.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1ada0_common_service_plan
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0, 0x503ad0, 0x11111111, 0x22222222, ctypes.byref(out))
    assert (out.call_count, out.conditional_call_included, out.continuation) == (17, 1, 0x1ae64)
    assert list(out.call_target) == [0xde630, 0xc8f10, 0x6fec0, 0x9b308, 0x6fec0, 0xc8f60, 0x9baa0, 0xde990, 0xbe1f0, 0xbd730, 0x11111111, 0x23980, 0xdf070, 0x26cb8, 0xbd810, 0x22222222, 0xdf070]
    assert (out.call_argument[6], out.call_argument[9], out.call_argument[13], out.call_argument[16]) == (0x503ad0, 0x503ad0, 0x5040d0, 0x5040d0)
    fn(1, 0x503ad0, 0x11111111, 0x22222222, ctypes.byref(out))
    assert (out.call_count, out.conditional_call_included, out.call_target[16]) == (16, 0, 0xdf070)
print("PASS: 0x1ada0 slot-10 common-service call plan")
