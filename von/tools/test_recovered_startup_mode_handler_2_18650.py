#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "helper_call", "helper_argument", "helper_argument_count", "mode_address",
        "mode_before", "mode_after", "phase_address", "phase_after",
        "mode_increment", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-mode-2-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode_handler_2_18650.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode_handler_2_18650
    fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
    out = Result()
    fn(0xffffffff, ctypes.byref(out))
    assert (out.helper_call, out.helper_argument, out.helper_argument_count,
            out.mode_address, out.mode_before, out.mode_after,
            out.phase_address, out.phase_after, out.mode_increment,
            out.return_target) == (0x1ccf8, 0, 1, 0x5039f4, 0xffffffff, 0,
                                    0x503a00, 0, 1, 0x18678)
    fn(7, ctypes.byref(out))
    assert out.mode_after == 8
print("PASS: 0x18650 startup mode handler 2")
