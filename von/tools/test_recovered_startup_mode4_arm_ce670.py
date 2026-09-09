#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "frame_adjust", "saved_register_bytes", "reset_call", "reset_argument",
        "startup_state_address", "startup_state_value", "phase_helper_call",
        "phase_helper_argument", "phase_address", "phase_before", "phase_after")]
    _fields_ += [("helper_call", ctypes.c_uint32 * 3)]
    _fields_ += [(n, ctypes.c_uint32) for n in ("helper_call_count", "result_address", "result_value", "template_source", "template_word_count", "record_base", "record_stride", "record_index")]
    _fields_ += [("record_word_offset", ctypes.c_uint32 * 21), ("record_word_value", ctypes.c_uint32 * 21), ("clear_address", ctypes.c_uint32 * 5)]
    _fields_ += [(n, ctypes.c_uint32) for n in ("clear_count",)]
    _fields_ += [("setup_call", ctypes.c_uint32 * 2), ("setup_argument", ctypes.c_uint32 * 2)]
    _fields_ += [(n, ctypes.c_uint32) for n in ("setup_count",)]
    _fields_ += [("workspace_address", ctypes.c_uint32 * 5)]
    _fields_ += [(n, ctypes.c_uint32) for n in ("workspace_clear_count", "workspace_phase_source", "workspace_table_source", "workspace_return_load_address", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-ce670-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_ce670.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_ce670
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Result)]
    words = (ctypes.c_uint32 * 21)(*range(21)); copied = (ctypes.c_uint32 * 21)(); out = Result()
    fn(3, 4, words, copied, ctypes.byref(out))
    assert (out.frame_adjust, out.startup_state_value, out.phase_after, out.helper_call_count, out.template_source, out.template_word_count, out.record_stride, out.record_index, out.record_word_offset[20], copied[20], out.return_target) == (16, 12, 5, 3, 0xc9220, 21, 0x154, 3, 80, 20, 0xce8ec)
    assert list(out.clear_address) == [0x503aac, 0x503a94, 0x503b34, 0x504134, 0x577138]
print("PASS: 0xce670 startup phase-table arm")
