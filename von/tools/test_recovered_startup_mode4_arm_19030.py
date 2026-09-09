#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "progress_address", "progress_before", "progress_after", "progress_was_zero",
        "reset_call", "setup_call", "setup_argument", "setup_performed",
        "setup_followup_call", "setup_followup_argument", "input_address", "input_value",
        "input_mask", "input_masked", "input_probe_call", "marker_value",
        "command_address", "command_value", "secondary_command_value",
        "device_word_address", "device_word", "hardware_mode_address", "hardware_mode",
        "device_match", "hardware_match_guard", "phase_address", "phase_before",
        "phase_after", "phase_incremented", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-19030-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_19030.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_19030
    fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0, 2, 8, 33, 0, 4, ctypes.byref(out))
    assert (out.progress_after, out.setup_performed, out.setup_argument, out.input_masked, out.command_value, out.device_match, out.phase_after, out.return_target) == (1, 1, 0x100b, 8, 33, 1, 5, 0x190c4)
    fn(7, 2, 0, 32, 1, 4, ctypes.byref(out))
    assert (out.progress_after, out.setup_performed, out.device_match, out.hardware_match_guard, out.phase_after) == (8, 0, 0, 0, 4)
print("PASS: 0x19030 startup phase-table arm")
