#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory(prefix="von-startup-mode4-table-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_dispatch_table_18b00.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_dispatch_table_18b00
    fn.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
    table = (ctypes.c_uint32 * 64)(); assert fn(table) == 1
    assert list(table[:6]) == [0x18c00, 0x18da0, 0x19030, 0xce670, 0xce8f0, 0x19660]
    assert list(table[28:35]) == [0xd3860, 0xd3960, 0xd3990, 0xd5eb0, 0xdc2b0, 0xdc3f0, 0xdc6d0]
    assert table[35] == 0 and all(value == 0 for value in table[36:])
print("PASS: 0x18b00 startup mode-4 dispatch table")
