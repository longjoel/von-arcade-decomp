#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]
class Plan(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in ("display_value", "counter_increment", "next_progress")]
with tempfile.TemporaryDirectory() as d:
    so = pathlib.Path(d) / "progress.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(so), str(ROOT / "von/i960/recovered_progress_mapping_2b870.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_progress_mapping_2b870
    fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    for progress in (0, 1, 15, 16, 17, 31, 32, 33, 127, 128, 0xffffffff):
        p = Plan(); fn(progress, ctypes.byref(p))
        expected = 0x200 - (progress << 5) if progress <= 15 else (2 * (progress - 32)) & 0xffffffff if progress <= 32 and progress & 1 else 0
        assert p.display_value == expected
        assert p.counter_increment == (progress == 128)
        assert p.next_progress == (progress + 1) & 0xffffffff
print("PASS: original 0x2b870 progress mapping vectors")
