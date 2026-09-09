#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "hardware_mode_address", "hardware_mode", "status34_address", "status34", "status23f2_address", "status23f2", "status38_address", "status38", "phase_address", "phase_before", "phase_after", "special_phase_value", "special_phase_written", "command_address", "command_value", "table_address", "table_index", "selected_handler", "handler_suppressed", "indirect_dispatch", "mode2_tail_entered", "mode2_candidate_address", "normal_tail_call", "normal_tail_result", "normal_tail_returned", "clear_helper_call", "phase_clear", "mode_address", "mode_before", "mode_after", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-mode-1-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode_handler_1_dispatch_2b9e0.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode_handler_1_dispatch_2b9e0
    fn.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Result)]
    table = (ctypes.c_uint32 * 32)(); table[29] = 0x2b500
    out = Result()
    fn(0, 0, 1, 1, 4, 7, 0, table, ctypes.byref(out))
    assert (out.command_value, out.table_index, out.selected_handler, out.handler_suppressed, out.indirect_dispatch, out.phase_after, out.special_phase_written, out.normal_tail_call, out.phase_clear, out.mode_after, out.return_target) == (16, 29, 0x2b500, 0, 1, 29, 1, 0x3ba0, 1, 8, 0x2bb58)
    table[4] = 0xe3ab0
    fn(2, 0, 0, 0, 4, 9, 0, table, ctypes.byref(out))
    assert (out.handler_suppressed, out.indirect_dispatch, out.mode2_tail_entered, out.phase_after, out.normal_tail_call) == (1, 0, 1, 1, 0)
    table[4] = 0
    table[29] = 0
    fn(0, 0, 0, 0, 4, 9, 1, table, ctypes.byref(out))
    assert (out.handler_suppressed, out.phase_after, out.normal_tail_returned, out.return_target) == (1, 1, 1, 0x2bb5c)
    fn(0, 0, 0, 1, 10, 9, 1, table, ctypes.byref(out))
    assert (out.special_phase_written, out.phase_before, out.phase_after) == (1, 10, 1)
    fn(0, 0, 0, 1, 4, 9, 1, table, ctypes.byref(out))
    assert (out.special_phase_written, out.phase_after) == (0, 1)
    fn(0, 0, 1, 1, 30, 9, 1, table, ctypes.byref(out))
    assert (out.special_phase_written, out.phase_after) == (0, 1)
print("PASS: 0x2b9e0 startup mode-handler 1 dispatch")
