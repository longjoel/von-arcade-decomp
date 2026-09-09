#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "ready_address", "ready_value", "hardware_mode_address", "hardware_mode",
        "pending_address", "pending_value", "timing_address", "timing_before",
        "timing_after", "timing_threshold", "threshold_exceeded", "phase_address", "phase_before",
        "phase_after", "fixed_timing_pointer", "fixed_workspace_pointer",
        "timing_publication_address", "timing_publication_value",
        "workspace_publication_address", "workspace_publication_value",
        "common_completion_call", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1a4a0-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1a4a0_prefix.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1a4a0_prefix
    fn.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Result)]
    out = Result(); fn(0, 1, 0, 10, 4, ctypes.byref(out))
    assert (out.fixed_timing_pointer, out.fixed_workspace_pointer, out.timing_after, out.phase_after, out.timing_publication_address, out.workspace_publication_address, out.return_target) == (0x5024fe, 0x502500, 0, 4, 0, 0, 0x1a578)
    fn(1, 0, 0, 0xeff, 4, ctypes.byref(out))
    assert (out.threshold_exceeded, out.timing_after, out.phase_after, out.timing_publication_address, out.workspace_publication_value) == (0, 0xf00, 5, 0x5032fe, 0xf00)
    fn(1, 0, 0, 0x80000000, 4, ctypes.byref(out))
    assert (out.threshold_exceeded, out.timing_after, out.phase_after) == (0, 0x80000001, 5)
    fn(0, 0, 1, 0x1000, 4, ctypes.byref(out))
    assert (out.threshold_exceeded, out.timing_after, out.phase_after, out.fixed_timing_pointer, out.fixed_workspace_pointer) == (0, 0x1000, 4, 0, 0)
    fn(1, 0, 0, 0x10, 0x8000, ctypes.byref(out))
    assert (out.timing_publication_value, out.workspace_publication_value) == (0xffff8001, 0x11)
print("PASS: 0x1a4a0 startup phase-table prefix")
