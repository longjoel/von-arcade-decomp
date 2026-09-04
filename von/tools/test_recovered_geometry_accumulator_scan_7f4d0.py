#!/usr/bin/env python3
import ctypes,pathlib,subprocess,tempfile
root=pathlib.Path(__file__).resolve().parents[2]; src=root/'von/i960/recovered_geometry_accumulator_scan_7f4d0.c'
with tempfile.TemporaryDirectory() as d:
 so=pathlib.Path(d)/'scan.so'; subprocess.run(['cc','-shared','-fPIC','-O2','-I',str(root/'von/i960'),'-o',str(so),str(src)],check=True); f=ctypes.CDLL(str(so)).recovered_geometry_accumulator_scan_7f4d0; f.argtypes=[ctypes.POINTER(ctypes.c_uint32)]*4; f.restype=ctypes.c_uint32
 A=(ctypes.c_uint32*32)(); B=(ctypes.c_uint32*32)(); M=(ctypes.c_uint32*32)(*[50-i for i in range(32)]); out=ctypes.c_uint32(100)
 A[2]=7; B[2]=11; M[2]=40; A[3]=7; B[3]=12; M[3]=1; A[4]=0; B[4]=2; M[4]=0
 assert f(A,B,M,ctypes.byref(out))==2 and out.value==40
 A[1]=3; B[1]=3; M[1]=2; assert f(A,B,M,ctypes.byref(out))==1 and out.value==2
print('recovered geometry 0x7f4d0 accumulator-scan fixtures: ok')
