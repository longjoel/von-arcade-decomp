#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "status_address", "status_word", "status_threshold", "status_high_path",
        "record_helper_address", "record_helper_call_count", "record_helper_argument0",
        "record_helper_argument1", "controller_address", "controller_word", "controller_bit4_set",
        "text_service_address", "text_string_address", "phase_continuation",
        "high_status_continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1a5cc-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1a5cc_status_gate.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1a5cc_status_gate
    fn.argtypes = [ctypes.c_uint32] * 2 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0xf423e, 0, ctypes.byref(out))
    assert (out.status_high_path, out.record_helper_call_count, out.phase_continuation) == (0, 0, 0x1a620)
    fn(0xf423f, 0, ctypes.byref(out))
    assert (out.status_high_path, out.record_helper_call_count, out.record_helper_argument0, out.record_helper_argument1, out.controller_bit4_set, out.text_service_address, out.high_status_continuation) == (1, 1, 6, 3, 0, 0x1d1f0, 0x1a7c8)
    fn(0xf423f, 0x10, ctypes.byref(out))
    assert (out.controller_bit4_set, out.text_service_address, out.text_string_address) == (1, 0x1d210, 0x1a490)
print("PASS: 0x1a5cc slot-10 status gate")
