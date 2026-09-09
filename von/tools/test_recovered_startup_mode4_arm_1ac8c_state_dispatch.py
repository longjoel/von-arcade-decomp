#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "state_address", "state_value", "state_zero_target", "state_one_target",
        "state_two_target", "state_five_target", "generic_target", "selected_target",
        "generic_selected")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1ac8c-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1ac8c_state_dispatch.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1ac8c_state_dispatch
    fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
    out = Result()
    for state, target in ((0, 0x1ad14), (1, 0x1ace0), (2, 0x1ad5c), (5, 0x1acac), (3, 0x1ada0), (0xffffffff, 0x1ada0)):
        fn(state, ctypes.byref(out))
        assert out.selected_target == target
        assert out.generic_selected == (1 if state not in (0, 1, 2, 5) else 0)
print("PASS: 0x1ac8c slot-10 state dispatch")
