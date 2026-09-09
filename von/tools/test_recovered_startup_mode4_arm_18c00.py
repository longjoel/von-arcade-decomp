#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "state_address", "state_before", "state_after", "initialization_call", "initialization_argument", "initialization_performed", "reset_call", "progress_call", "progress_call_count", "device_word_address", "device_word", "check_mask", "checks_required", "checks_passed")]
    _fields_ += [("check_offsets", ctypes.c_uint32 * 7)]
    _fields_ += [(n, ctypes.c_uint32) for n in ("special_device_word", "special_device_exception", "success_path", "success_progress_address", "success_progress_value", "record_state_call", "record_state_first", "record_state_second")]
    _fields_ += [("formatter_call", ctypes.c_uint32 * 3)]
    _fields_ += [(n, ctypes.c_uint32) for n in ("formatter_call_count", "ready_address", "ready_after", "command_address", "command_value", "phase_address", "phase_before", "phase_after", "phase_incremented", "fallback_path", "cleanup_address", "cleanup_value", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-18c00-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_18c00.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_18c00
    fn.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Result)]
    out = Result(); fn(0, 16, 1, 0x7f, 5, ctypes.byref(out))
    assert (out.initialization_performed, out.checks_required, out.checks_passed, out.success_path, out.formatter_call_count, out.success_progress_value, out.ready_after, out.phase_after, out.fallback_path, out.return_target) == (1, 7, 7, 0, 0, 0x293, 0, 3, 1, 0x18d9c)
    fn(1, 0x52, 1, 0x3f, 5, ctypes.byref(out))
    assert (out.special_device_exception, out.checks_required, out.checks_passed, out.success_path, out.fallback_path, out.command_value, out.phase_after, out.state_after) == (1, 6, 6, 1, 0, 35, 6, 1)
    fn(4, 0, 1, 0, 5, ctypes.byref(out))
    assert (out.initialization_performed, out.success_path, out.fallback_path, out.state_after, out.phase_after) == (0, 0, 0, 5, 5)
print("PASS: 0x18c00 startup phase-table arm")
