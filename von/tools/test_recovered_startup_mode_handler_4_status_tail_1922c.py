#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in ("status_address", "status_word", "maintenance_call", "maintenance_call_count", "maintenance_phase_low", "maintenance_phase_high", "copy_call", "copy_source", "copy_destination", "copy_length", "phase_address", "phase_before", "phase_after", "ready_address", "ready_value", "hardware_mode_address", "hardware_mode_value", "bank_window_low", "bank_window_high", "bank_window_passed")]
    _fields_ += [(n, ctypes.c_uint32 * 5) for n in ("primary_source_address", "primary_value")]
    _fields_ += [(n, ctypes.c_uint32 * 3) for n in ("fallback_source_address", "fallback_value")]
    _fields_ += [(n, ctypes.c_uint32) for n in ("selected_bank",)]
    _fields_ += [(n, ctypes.c_uint32 * 3) for n in ("publication_address", "publication_value")]
    _fields_ += [(n, ctypes.c_uint32) for n in ("publication_count", "table_address", "table_index", "selected_handler", "dispatch_taken", "mode_address", "mode_before", "mode_after", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-mode-4-tail-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode_handler_4_status_tail_1922c.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode_handler_4_status_tail_1922c
    fn.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(ctypes.c_uint32)] * 3 + [ctypes.POINTER(Result)]
    table = (ctypes.c_uint32 * 64)(); table[5] = 0x123456
    primary = (ctypes.c_uint32 * 5)(1, 2, 3, 0x104, 0x205)
    fallback = (ctypes.c_uint32 * 3)(0x306, 0x407, 0x508)
    out = Result()
    fn(1, 5, 1, 1, 9, table, primary, fallback, ctypes.byref(out))
    assert (out.bank_window_low, out.bank_window_high) == (7, 10)
    assert (out.maintenance_call_count, out.copy_length, out.bank_window_passed, list(out.publication_value), out.table_index, out.selected_handler, out.dispatch_taken, out.phase_after, out.return_target) == (0, 20, 0, [0x306, 7, 8], 5, 0x123456, 1, 5, 0x19358)
    fn(1, 6, 1, 1, 9, table, primary, fallback, ctypes.byref(out))
    assert out.bank_window_passed == 0
    fn(1, 7, 1, 1, 9, table, primary, fallback, ctypes.byref(out))
    assert (out.bank_window_passed, list(out.publication_value), out.table_index, out.selected_handler, out.dispatch_taken, out.phase_after, out.return_target) == (1, [3, 4, 5], 7, 0, 0, 0, 0x19350)
    table[5] = 0
    fn(1, 15, 0, 0, 9, table, primary, fallback, ctypes.byref(out))
    assert (out.maintenance_call_count, out.bank_window_passed, list(out.publication_value), out.phase_after, out.mode_after, out.return_target) == (1, 0, [0x306, 7, 8], 0, 10, 0x19350)
print("PASS: 0x1922c startup mode-handler 4 status tail")
