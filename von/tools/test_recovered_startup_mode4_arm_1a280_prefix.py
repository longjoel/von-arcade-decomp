#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "progress_address", "progress_before", "progress_after", "progress_threshold", "threshold_match", "cleared_address", "cleared_value", "setup_call", "setup_argument", "setup_performed", "ready_address", "ready_value", "hardware_mode_address", "hardware_mode", "device_word_address", "device_word", "register_18_value", "command_address", "command_value", "ready_marker_address", "ready_marker_value", "record_helper_call", "record_helper_first", "record_helper_second", "probe_call", "probe_argument", "phase_address", "phase_before", "phase_after", "common_continuation", "gate_path")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1a280-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1a280_prefix.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1a280_prefix
    fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Result)]
    out = Result(); fn(0, 0, 0, 0, 2, 4, ctypes.byref(out))
    assert (out.progress_after, out.setup_performed, out.command_value, out.gate_path, out.ready_marker_value, out.record_helper_first, out.record_helper_second, out.phase_after, out.common_continuation) == (0xffffffff, 0, 33, 1, 1, 14, 16, 5, 0x1a3dc)
    fn(7, 1, 1, 33, 2, 4, ctypes.byref(out))
    assert (out.threshold_match, out.gate_path, out.ready_value, out.record_helper_second, out.phase_after, out.common_continuation) == (0, 2, 1, 18, 5, 0x1a3dc)
    fn(31, 1, 0, 0, 2, 4, ctypes.byref(out))
    assert (out.threshold_match, out.setup_performed, out.gate_path, out.common_continuation) == (1, 0x1, 0, 0x1a3fc)
print("PASS: 0x1a280 startup phase-table prefix")
