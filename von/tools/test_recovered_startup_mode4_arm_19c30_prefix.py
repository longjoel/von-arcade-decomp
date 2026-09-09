#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "register_restore_quad", "marker_address", "marker_value", "workspace_clear_address", "workspace_clear_value", "setup_call", "setup_argument", "phase_flag_address", "phase_flag_value", "phase_flag_helper_call", "phase_code", "phase_code_address", "phase_code_source", "phase_code_value", "phase_code_sentinel", "status_address", "status_value", "status_threshold", "status_above_threshold", "record_helper_call", "record_helper_first", "record_helper_second", "result_helper_call", "result_helper_argument", "ready_address", "ready_value", "startup_counter_address", "startup_counter_value", "register_17_value", "register_29_value", "arithmetic_divisor", "arithmetic_constant", "arithmetic_remainder", "arithmetic_quotient", "arithmetic_scaled_remainder", "arithmetic_result", "math_helper_call", "math_result_address", "hardware_mode_address", "hardware_mode", "ready_split", "return_or_continuation")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-19c30-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_19c30_prefix.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_19c30_prefix
    fn.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Result)]
    out = Result(); fn(0, 0xf423e, 0, 3, 1, 17, 29, ctypes.byref(out))
    assert (out.marker_value, out.workspace_clear_value, out.phase_code, out.status_above_threshold, out.arithmetic_remainder, out.arithmetic_quotient, out.arithmetic_scaled_remainder, out.ready_split, out.return_or_continuation) == (0xff, 0, 100, 0, 0, 16, 0, 1, 0x19d20)
    fn(1, 0xf5000, 1, 5, 0, 17, 29, ctypes.byref(out))
    assert (out.phase_code, out.status_above_threshold, out.ready_split, out.record_helper_first, out.record_helper_second) == (105, 1, 0, 6, 3)
    fn(0, 1213, 0, 27, 0, 9, 29, ctypes.byref(out))
    assert (out.arithmetic_divisor, out.arithmetic_constant, out.arithmetic_remainder, out.arithmetic_scaled_remainder, out.arithmetic_result) == (27, 40, 13, 13 * 99, (13 * 99) // 40)
print("PASS: 0x19c30 startup phase-table prefix")
