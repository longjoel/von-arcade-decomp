#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Record(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in ("id", "line", "text_length", "sentinel")]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "setup_call", "device_register", "device_command", "device_command_count", "phase_address",
        "phase_before", "phase_after", "clear_call", "record_state_call", "record_state_count",
        "table_address", "record_count", "character_call", "character_count", "progress_address",
        "progress_before", "progress_after", "status_address", "status_value", "table_walk_performed",
        "completion_flag_address", "completion_flag_after", "mode_address", "mode_before", "mode_after",
        "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-mode-0-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode_handler_0_3c40.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode_handler_0_3c40
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Record), ctypes.POINTER(Result)]
    records = (Record * 64)(); records[0] = Record(1, 2, 4, 0); records[1] = Record(3, 4, 0, 0); records[2].sentinel = 1
    out = Result()
    fn(0, 0, 0x234, 7, records, ctypes.byref(out))
    assert (out.setup_call, out.device_command, out.table_address, out.table_walk_performed, out.record_count, out.record_state_count, out.character_call, out.character_count, out.progress_after, out.phase_after, out.mode_after, out.return_target) == (0x294b0, 8, 0x2ea2918, 1, 2, 2, 0x1cc40, 4, 0x233, 0, 7, 0x3d60)
    fn(2, 1, 0, 0xffffffff, records, ctypes.byref(out))
    assert (out.table_walk_performed, out.progress_after, out.completion_flag_after, out.phase_after, out.mode_after) == (0, 0xffffffff, 1, 0, 0)
    fn(0, 1, 1, 7, records, ctypes.byref(out))
    assert (out.table_walk_performed, out.completion_flag_after, out.progress_before, out.progress_after, out.phase_after, out.mode_after) == (0, 1, 0x234, 0x233, 0, 7)
print("PASS: 0x3c40 startup UI record walker")
