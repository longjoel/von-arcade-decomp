#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "reset_call", "phase_helper_call", "phase_helper_argument", "ready_address",
        "ready_value", "status_address", "status_value", "status_command_address",
        "status_command_value", "command_address", "command_value", "command_register_value",
        "ready_adjustment", "phase_address", "phase_before", "phase_after",
        "progress_clear_address", "progress_clear_value", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-19660-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_19660.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_19660
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Result)]
    out = Result(); fn(0, 0x1234, 2, 7, ctypes.byref(out))
    assert (out.reset_call, out.status_command_value, out.command_value, out.ready_adjustment, out.phase_after, out.progress_clear_value, out.return_target) == (0x1c618, 0x1234, 33, 0, 8, 0, 0x196b8)
    fn(1, 0xab, 2, 7, ctypes.byref(out))
    assert (out.command_value, out.ready_adjustment, out.phase_after) == (34, 1, 8)
print("PASS: 0x19660 startup phase-table arm")
