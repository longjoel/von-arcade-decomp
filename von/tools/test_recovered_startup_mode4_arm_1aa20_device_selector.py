#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "device_address", "device_word", "callback_register", "state_address", "state_value",
        "command_address", "command_value", "phase_address", "phase_before", "phase_after",
        "selected", "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1aa20-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1aa20_device_selector.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1aa20_device_selector
    fn.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Result)]
    out = Result()
    for device, state, command in ((0x40, 1, 0x41), (0x42, 2, 0x42), (0x43, 5, 0x43)):
        fn(device, 0x77, 9, ctypes.byref(out))
        assert (out.selected, out.state_value, out.command_value, out.phase_after, out.continuation) == (1, state, command, 10, 0x1ac44)
    fn(0x41, 0x77, 9, ctypes.byref(out))
    assert (out.selected, out.state_value, out.command_value) == (1, 0x77, 0x40)
    fn(0x44, 0x77, 9, ctypes.byref(out))
    assert (out.selected, out.phase_after, out.continuation) == (0, 9, 0x1ac50)
print("PASS: 0x1aa20 slot-10 device selector")
