#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "phase_address", "phase_before", "phase_after", "saved_status_address", "saved_status",
        "timing_call", "timing_result", "timing_limit", "timing_state_address", "timing_state_after")]
    _fields_ += [("clear_address", ctypes.c_uint32 * 3)]
    _fields_ += [(n, ctypes.c_uint32) for n in ("clear_count", "message_call", "message_count")]
    _fields_ += [("message_x", ctypes.c_uint32 * 5), ("message_y", ctypes.c_uint32 * 5), ("message_string", ctypes.c_uint32 * 5)]
    _fields_ += [(n, ctypes.c_uint32) for n in (
        "gate_call", "gate_result", "reset_call", "terminal_service_count", "startup_flag_address",
        "startup_flag_after", "device_command_address", "device_command", "saved_state_address",
        "saved_state", "cmpible_taken", "cmpibl_taken", "transition_mode_value", "transition_mode_address", "transition_phase_address",
        "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-mode-7-") as d:
    so = Path(d) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode_handler_7_f3d30.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode_handler_7_f3d30
    fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0, 1, 0x2711, 9, 0, 0, ctypes.byref(out))
    assert (out.phase_after, out.message_count, out.message_call, out.message_x[0], out.message_y[0], out.message_string[0]) == (1, 5, 0xeaeb0, 16, 15, 0xf3ca0)
    fn(0, 1, 0x2710, 9, 0, 0, ctypes.byref(out))
    assert (out.phase_after, out.message_count, out.clear_count) == (2, 0, 3)
    fn(1, 1, 0, 0, 0, 0, ctypes.byref(out))
    assert (out.gate_call, out.phase_after, out.reset_call) == (0xeade8, 2, 0x1c618)
    fn(1, 1, 0, 1, 0, 0, ctypes.byref(out))
    assert out.phase_after == 1
    fn(2, 0, 0, 1, 0, 7, ctypes.byref(out))
    assert (out.terminal_service_count, out.cmpible_taken, out.cmpibl_taken, out.transition_mode_value, out.phase_after, out.return_target) == (3, 1, 1, 0xffffffff, 0, 0xf3ec0)
    fn(2, 1, 0, 1, 1, 0xffffffff, ctypes.byref(out))
    assert (out.cmpible_taken, out.cmpibl_taken, out.transition_mode_value) == (0, 0, 0)
print("PASS: 0xf3d30 startup mode-handler 7")
