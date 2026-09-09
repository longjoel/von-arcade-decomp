#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "counter_address", "counter_before", "controller_byte_address", "controller_byte",
        "controller_word_address", "controller_word", "helper_address", "helper_call_count",
        "helper_argument", "helper_argument_valid", "status_continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1a578-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1a578_progress_gate.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1a578_progress_gate
    fn.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0x7fffffff, 0, 0, ctypes.byref(out))
    assert (out.helper_call_count, out.helper_argument, out.helper_argument_valid) == (0, 0, 0)
    fn(0x80000000, 0, 0, ctypes.byref(out))
    assert (out.helper_call_count, out.helper_argument, out.helper_argument_valid) == (1, 0x7fffffff, 1)
    fn(0x80000000, 65, 0x21, ctypes.byref(out))
    assert out.helper_call_count == 0
    fn(0x80000000, 65, 0x30, ctypes.byref(out))
    assert (out.helper_call_count, out.helper_argument, out.helper_argument_valid, out.status_continuation) == (1, 16, 1, 0x1a5cc)
print("PASS: 0x1a578 slot-10 progress/controller gate")
