#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "countdown_address", "countdown_before", "countdown_after", "record_result_address",
        "record_index", "record_stride")]
    _fields_ += [("helper_call", ctypes.c_uint32 * 3)]
    _fields_ += [(n, ctypes.c_uint32) for n in ("helper_call_count", "record_table_address", "record_base", "gate_field_4c", "gate_field_0c", "gate_status_a4", "gate_field_4", "initialization_gate", "initialized_entry_count", "entry_stride", "entry_base", "entry_zero_offset", "entry_count_offset", "link_source", "link_destination", "link_count_incremented")]
    _fields_ += [("record_link_offset", ctypes.c_uint32 * 5)]
    _fields_ += [(n, ctypes.c_uint32) for n in ("record_count_offset", "record_count_after", "bookkeeping_call", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-ce8f0-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_ce8f0.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_ce8f0
    fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Result)]
    count = ctypes.c_uint32(); out = Result()
    fn(2, 0, 0, 0, 0x100, 4, ctypes.byref(count), ctypes.byref(out))
    assert (out.countdown_after, out.record_base, out.helper_call_count, out.initialization_gate, out.initialized_entry_count, out.entry_stride, count.value, out.bookkeeping_call, out.return_target) == (1, 0x51c858, 3, 1, 9, 0x54, 5, 0x22c78, 0xceab4)
    fn(2, 3, 1, 0, 0, 31, ctypes.byref(count), ctypes.byref(out))
    assert (out.countdown_after, out.initialization_gate, out.initialized_entry_count, count.value) == (3, 0, 0, 32)
print("PASS: 0xce8f0 startup phase-table arm")
