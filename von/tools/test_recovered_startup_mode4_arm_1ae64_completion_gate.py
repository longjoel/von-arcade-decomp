#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "ready_address", "ready_value", "status_address", "status_word", "status_threshold",
        "result_r5", "result_r6", "record_pointer", "buffer_pointer", "call_count")]
    _fields_ += [("call_target", ctypes.c_uint32 * 7), ("call_argument", ctypes.c_uint32 * 7)]
    _fields_ += [(n, ctypes.c_uint32) for n in (
        "completion_service", "completion_argument", "completion_normal", "completion_exception",
        "shared_service", "shared_call_count", "continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1ae64-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1ae64_completion_gate.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1ae64_completion_gate
    fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Result)]
    out = Result()
    fn(1, 0, 0, 0, 0x503ad0, 0x5040d0, ctypes.byref(out))
    assert (out.call_count, list(out.call_target), out.completion_argument, out.call_argument[0], out.call_argument[5], out.shared_service, out.continuation) == (7, [0xbece0, 0x9b320, 0x41f20, 0xc5530, 0x6fec0, 0x71080, 0x23d60], 0, 0x503ad0, 0x503ad0, 0x87f60, 0x1aee4)
    fn(0, 0, 0, 0, 0, 0, ctypes.byref(out))
    assert out.completion_argument == 1
    fn(1, 0xf423f, 0, 0, 0, 0, ctypes.byref(out))
    assert out.completion_argument == 1
    fn(1, 0xf423e, 0, 0, 0, 0, ctypes.byref(out))
    assert out.completion_argument == 0
    fn(1, 0x80000000, 0, 0, 0, 0, ctypes.byref(out))
    assert out.completion_argument == 1
    fn(1, 0, 1, 0, 0, 0, ctypes.byref(out))
    assert out.completion_argument == 1
print("PASS: 0x1ae64 slot-10 completion gate")
