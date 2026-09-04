#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile
root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_indexed_packet_8d5d0.c"
class I(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in ("value_0", "value_2", "value_4", "value_6", "value_8", "value_10", "signed_count")]
class P(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 10), ("fifo_count", ctypes.c_uint32), ("xor_mask", ctypes.c_uint32), ("normalized_count", ctypes.c_uint32), ("next_record_offset", ctypes.c_uint32)]
with tempfile.TemporaryDirectory() as d:
    so = pathlib.Path(d) / "indexed.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"), "-o", str(so), str(source)], check=True)
    f = ctypes.CDLL(str(so)).recovered_geometry_indexed_packet_8d5d0
    f.argtypes = [ctypes.POINTER(I), ctypes.POINTER(P)]
    p = P(); i = I(1, 2, 3, 4, 5, 6, 1); f(ctypes.byref(i), ctypes.byref(p))
    assert list(p.fifo_word) == [20, 0xffff, 21, 0xfffe, 22, 0xfffd, 47, 0x8004, 0x8005, 0x8006]
    assert p.fifo_count == 10 and p.xor_mask == 0x8000 and p.next_record_offset == 12
    i.signed_count = 2; f(ctypes.byref(i), ctypes.byref(p)); assert p.xor_mask == 0 and p.fifo_word[7] == 4
print("recovered geometry 0x8d5d0 indexed-packet fixtures: ok")
