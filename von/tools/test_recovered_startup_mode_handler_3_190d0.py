#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "setup_call", "setup_argument", "reset_call", "phase_helper_call", "enabled_byte_address",
        "enabled_byte_value", "video_base_address", "video_base_value", "upload_base_address",
        "upload_base_value")]
    _fields_ += [("clear_address", ctypes.c_uint32 * 9), ("clear_count", ctypes.c_uint32)]
    _fields_ += [(name, ctypes.c_uint32) for name in ("mode_address", "mode_before", "mode_after", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-mode-3-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode_handler_3_190d0.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode_handler_3_190d0
    fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
    out = Result()
    fn(0xffffffff, ctypes.byref(out))
    assert (out.setup_call, out.setup_argument, out.reset_call, out.phase_helper_call, out.enabled_byte_address, out.enabled_byte_value, out.clear_count, out.mode_after, out.return_target) == (0x2a4e0, 0x1111, 0x1c618, 0x1bda0, 0x504b96, 1, 9, 0, 0x19170)
    assert list(out.clear_address) == [0x503a84, 0x503a80, 0x503a88, 0x504c98, 0x503a8c, 0x503a90, 0x503a1c, 0x504c90, 0x503ac0]
print("PASS: 0x190d0 startup mode handler 3")
