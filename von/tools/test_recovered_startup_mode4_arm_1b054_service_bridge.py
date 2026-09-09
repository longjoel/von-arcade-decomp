#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "ready_address", "ready_value", "record_pointer", "callback_target_a", "callback_target_b",
        "state_address", "state_value", "first_numerator_address", "first_numerator_raw",
        "first_numerator_signed", "second_numerator_address", "second_numerator_raw",
        "second_numerator_signed", "first_timer_address", "second_timer_address", "first_timer_value",
        "second_timer_value", "call_count", "conditional_call_included")]
    _fields_ += [("call_target", ctypes.c_uint32 * 24), ("call_argument", ctypes.c_uint32 * 24)]
    _fields_ += [("continuation", ctypes.c_uint32)]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1b054-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1b054_service_bridge.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1b054_service_bridge
    fn.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0, 0x503ad0, 0x11111111, 0x22222222, 2, 0xfffe, 0x8001, ctypes.byref(out))
    assert (out.call_count, out.conditional_call_included, out.continuation) == (24, 1, 0x1b160)
    assert list(out.call_target) == [0xde630, 0xc8f10, 0x6fec0, 0x9b308, 0x6fec0, 0xc8f60, 0x9baa0, 0xde990, 0xbe1f0, 0xbd730, 0x11111111, 0xdf070, 0x26cb8, 0xbd810, 0x22222222, 0xdf070, 0xbece0, 0x9b320, 0x41f20, 0xc5530, 0x6fec0, 0x71080, 0x23d60, 0x8d0b8]
    assert (out.first_numerator_signed, out.second_numerator_signed, out.first_timer_value, out.second_timer_value) == (0xfffffffe, 0xffff8001, 0xfffffffe, 0xffff8001)
    assert (out.call_argument[6], out.call_argument[12], out.call_argument[21], out.call_argument[23]) == (0x503ad0, 0x5040d0, 0x503ad0, 2)
    fn(1, 0, 0, 0, 5, 0, 0, ctypes.byref(out))
    assert out.call_count == 23 and out.conditional_call_included == 0 and out.call_target[15] == 0xdf070
print("PASS: 0x1b054 slot-11 service bridge")
