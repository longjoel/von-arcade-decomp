#!/usr/bin/env python3
import ctypes,pathlib,subprocess,tempfile
root=pathlib.Path(__file__).resolve().parents[2]; src=root/'von/i960/recovered_geometry_accumulator_transition_7f5d0.c'
class I(ctypes.Structure): _fields_=[(n,ctypes.c_uint32) for n in ('state170','state172','mode64','gate504d68','gate504da4','gate504dc8','candidate_pass','metric_pass','threshold_pass')]
class P(ctypes.Structure): _fields_=[('eligible',ctypes.c_uint32),('action_state',ctypes.c_uint32),('action_code',ctypes.c_uint32)]
with tempfile.TemporaryDirectory() as d:
 so=pathlib.Path(d)/'t.so'; subprocess.run(['cc','-shared','-fPIC','-O2','-I',str(root/'von/i960'),'-o',str(so),str(src)],check=True); f=ctypes.CDLL(str(so)).recovered_geometry_accumulator_transition_7f5d0; f.argtypes=[ctypes.POINTER(I),ctypes.POINTER(P)]
 i=I(3,1,3,7,0,0,1,1,1); p=P(); f(ctypes.byref(i),ctypes.byref(p)); assert (p.eligible,p.action_state,p.action_code)==(1,1,10)
 i.mode64=4; i.gate504d68=4; f(ctypes.byref(i),ctypes.byref(p)); assert (p.action_state,p.action_code)==(4,4)
print('recovered geometry 0x7f5d0 transition fixtures: ok')
