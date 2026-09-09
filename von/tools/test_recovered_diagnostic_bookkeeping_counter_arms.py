#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
 _fields_=[("matrix_renderer",ctypes.c_uint32),("pattern_address",ctypes.c_uint32),("pattern_value",ctypes.c_uint32),("clear_address",ctypes.c_uint32),("probe_call",ctypes.c_uint32),("probe_result",ctypes.c_uint32),("field_address",ctypes.c_uint32),("field_before",ctypes.c_uint32),("field_after",ctypes.c_uint32),("modulus",ctypes.c_uint32),("zero_replacement",ctypes.c_uint32),("service_state_address",ctypes.c_uint32),("service_state_value",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
 with tempfile.TemporaryDirectory(prefix="von-counter-arms-") as d:
  so=Path(d)/"x.so";subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_bookkeeping_counter_a_arm_f2d00.c"),str(ROOT/"von/i960/recovered_diagnostic_bookkeeping_counter_b_arm_f2d70.c")],check=True)
  lib=ctypes.CDLL(str(so));a=lib.recovered_diagnostic_bookkeeping_counter_a_arm_f2d00;b=lib.recovered_diagnostic_bookkeeping_counter_b_arm_f2d70;a.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(Result)];b.argtypes=a.argtypes;ao=Result();bo=Result();a(1,9,ctypes.byref(ao));b(1,9,ctypes.byref(bo));assert (ao.field_after,ao.pattern_address,ao.clear_address,ao.return_target)==(1,0x1004714,0x1004614,0xf2d64);assert (bo.field_after,bo.pattern_address,bo.clear_address,bo.return_target)==(1,0x1004c14,0x1004714,0xf2dd4);print("PASS: 0xf2d00/0xf2d70 bookkeeping counter arms")
if __name__=="__main__":main()
