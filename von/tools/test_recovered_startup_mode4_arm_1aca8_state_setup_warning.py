#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "state_address", "state_value", "ready_address", "ready_value", "row_address", "row_value",
        "hardware_address", "hardware_mode", "setup_helper", "setup_call_count", "setup_argument",
        "warning_service", "warning_call_count", "warning_code", "recognized_state", "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1aca8-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1aca8_state_setup_warning.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1aca8_state_setup_warning
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Result)]
    out = Result()
    for state, setup, warning in ((0, 0x1314, 0x93), (1, 0x1315, 0x97), (2, 0x1313, 0x97), (5, 0x1312, 0x97)):
        fn(state, 0, 9, 0, ctypes.byref(out))
        assert (out.recognized_state, out.setup_argument, out.setup_call_count, out.warning_code, out.warning_call_count, out.continuation) == (1, setup, 0, warning, 1, 0x1ada0)
        fn(state, 1, 9, 1, ctypes.byref(out))
        assert (out.setup_call_count, out.warning_code) == (1, warning + 8)
    fn(5, 0, 8, 1, ctypes.byref(out))
    assert (out.setup_argument, out.setup_call_count, out.warning_code) == (0x1312, 1, 0x9f)
    fn(0, 0, 8, 0, ctypes.byref(out))
    assert (out.setup_call_count, out.warning_code) == (1, 0x93)
    fn(7, 0, 9, 0, ctypes.byref(out))
    assert (out.recognized_state, out.setup_call_count, out.warning_call_count, out.continuation) == (0, 0, 0, 0x1ada0)
print("PASS: 0x1aca8 slot-10 state setup/warning arms")
