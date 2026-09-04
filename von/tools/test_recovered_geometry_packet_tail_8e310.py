#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile
root=pathlib.Path(__file__).resolve().parents[2]; src=root/'von/i960/recovered_geometry_packet_tail_8e310.c'
class I(ctypes.Structure): _fields_=[(n,ctypes.c_uint32) for n in ('vector_1','vector_3','vector_5','byte_m2','byte_m1','byte_0','frame_readback')]
class P(ctypes.Structure): _fields_=[('fifo_word',ctypes.c_uint32*10),('fifo_count',ctypes.c_uint32)]
with tempfile.TemporaryDirectory() as d:
 so=pathlib.Path(d)/'tail.so'; subprocess.run(['cc','-shared','-fPIC','-O2','-I',str(root/'von/i960'),'-o',str(so),str(src)],check=True)
 f=ctypes.CDLL(str(so)).recovered_geometry_packet_tail_8e310; f.argtypes=[ctypes.POINTER(I),ctypes.POINTER(P)]
 i=I(0x10001,0x20002,0x30003,0xaaaa12,0xbbbb34,0xcccc56,0xdeadbeef); p=P(); f(ctypes.byref(i),ctypes.byref(p))
 assert list(p.fifo_word)==[5,1,2,3,46,0x12,0x34,0x56,0x1f,0xdeadbeef] and p.fifo_count==10
print('recovered geometry 0x8e310 packet-tail fixture: ok')
