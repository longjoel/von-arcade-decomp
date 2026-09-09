#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "device_word_address", "device_word", "primary_marker", "primary_command",
        "status_address", "status_value", "status_command", "progress_address",
        "progress_before", "progress_after", "progress_was_zero", "progress_triggered_setup",
        "input_address", "input_value", "input_mask", "input_masked", "input_probe_call")]
    _fields_ += [("setup_call", ctypes.c_uint32 * 3), ("setup_argument", ctypes.c_uint32 * 3)]
    _fields_ += [(n, ctypes.c_uint32) for n in ("setup_count", "ready_address", "ready_before", "ready_after", "command_address", "command_value", "phase_address", "phase_before", "phase_after", "workspace_clear_address", "workspace_clear_value", "workspace_pointer_address", "workspace_pointer_value", "branch_primary", "branch_status", "branch_32", "fallback_path", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-196c0-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_196c0.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_196c0
    fn.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Result)]
    out = Result(); fn(33, 2, 9, 0, 8, 0, 4, ctypes.byref(out))
    assert (out.branch_primary, out.progress_after, out.progress_triggered_setup, out.setup_count, out.command_value, out.ready_after, out.return_target) == (1, 1, 1, 3, 34, 1, 0x19740)
    fn(40, 2, 9, 7, 0, 1, 4, ctypes.byref(out))
    assert (out.branch_status, out.branch_32, out.fallback_path, out.command_value, out.phase_after, out.workspace_pointer_value, out.return_target) == (1, 0, 0, 0, 5, 0x5024fc, 0x1979c)
    fn(7, 2, 9, 7, 0, 1, 4, ctypes.byref(out))
    assert (out.fallback_path, out.ready_after, out.phase_after, out.workspace_pointer_value, out.return_target) == (1, 0, 5, 0x5024f8, 0x19820)
print("PASS: 0x196c0 startup phase-table arm")
