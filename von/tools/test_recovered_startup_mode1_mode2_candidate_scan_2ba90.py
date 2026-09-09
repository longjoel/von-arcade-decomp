#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "candidate_count", "candidate_first", "candidate_last", "candidate_stride_words", "candidate_stride_bytes",
        "candidate_source_address", "candidate_publish_address", "candidate_match_value", "candidate_delta",
        "candidate_mask", "candidate_match_count", "selected_candidate", "selected_value", "published", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-mode2-scan-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode1_mode2_candidate_scan_2ba90.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode1_mode2_candidate_scan_2ba90
    fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Result)]
    values = (ctypes.c_uint32 * 256)(); values[3] = 31; values[2] = 35; values[1] = 32
    out = Result(); fn(4, values, ctypes.byref(out))
    assert (out.candidate_first, out.candidate_stride_words, out.candidate_stride_bytes, out.candidate_source_address, out.candidate_match_value, out.candidate_delta, out.candidate_mask, out.candidate_match_count, out.selected_candidate, out.selected_value, out.published, out.return_target) == (3, 7, 0x700, 0x1a14002, 32, 34, 0xffff, 1, 2, 2, 1, 0x2bb28)
    values[2] = 0; values[1] = 0; values[0] = 0
    fn(4, values, ctypes.byref(out))
    assert (out.candidate_match_count, out.published) == (0, 0)
    values[0] = 32
    fn(4, values, ctypes.byref(out))
    assert (out.candidate_match_count, out.published) == (0, 0)
    fn(1, values, ctypes.byref(out))
    assert (out.candidate_match_count, out.selected_value, out.published) == (1, 0, 1)
print("PASS: 0x2ba90 mode-2 candidate scan")
