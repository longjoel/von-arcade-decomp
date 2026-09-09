#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class Result(ctypes.Structure):
    pass

Result._fields_ = [(name, ctypes.c_uint32) for name in (
    "setup_call", "setup_call_count", "device_register")] + [("device_word", ctypes.c_uint32 * 2)] + [(name, ctypes.c_uint32) for name in (
    "device_word_count", "ready_address", "ready_value", "ready_required", "device_status_address",
    "device_status_value", "device_status_required", "phase_address", "phase_value", "phase_low",
        "phase_high", "phase_window_passed", "special_phase_passed", "hardware_word_address",
    "hardware_word_before", "hardware_word_after", "hardware_mask", "hardware_setup_call",
    "marker_address", "marker_value")] + [("setup_argument", ctypes.c_uint32 * 2)] + [(name, ctypes.c_uint32) for name in (
    "setup_argument_count", "setup_argument_call", "phase_after", "ready_after", "tail_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-mode-4-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode_handler_4_prefix_19180.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode_handler_4_prefix_19180
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0, 33, 27, 0xffff, ctypes.byref(out))
    assert (list(out.device_word), out.phase_window_passed, out.special_phase_passed, out.hardware_word_after, out.marker_value, list(out.setup_argument), out.phase_after, out.ready_after, out.tail_target) == ([8, 16], 0, 1, 0xfffe, 32, [0x111b, 2], 5, 1, 0x1922c)
    fn(0, 33, 12, 0xffff, ctypes.byref(out))
    assert (out.phase_window_passed, out.phase_after) == (1, 5)
    fn(0, 33, 13, 0xffff, ctypes.byref(out))
    assert (out.phase_window_passed, out.special_phase_passed, out.phase_after) == (0, 0, 13)
    fn(1, 33, 8, 0, ctypes.byref(out))
    assert (out.phase_after, out.ready_after) == (8, 1)
print("PASS: 0x19180 startup mode handler 4 prefix")
