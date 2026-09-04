#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]
class Plan(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in ("node_next", "node_prev", "old_next", "new_tail")]
with tempfile.TemporaryDirectory() as d:
    so = pathlib.Path(d) / "append.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(so), str(ROOT / "von/i960/recovered_linked_list_append_298b8.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_linked_list_append_298b8
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    p = Plan(); fn(0x515120, 0x5150f0, 0x515090, ctypes.byref(p))
    assert (p.node_next, p.node_prev, p.old_next, p.new_tail) == (0x515090, 0x5150f0, 0x515120, 0x515120)
print("PASS: original 0x298b8 doubly-linked-list append contract")
