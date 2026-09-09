#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def build(name):
 class R(ctypes.Structure):
  _fields_=[("matrix_renderer",ctypes.c_uint32),("pattern_address",ctypes.c_uint32),("pattern_value",ctypes.c_uint32),("clear_address",ctypes.c_uint32),("probe_call",ctypes.c_uint32),("probe_result",ctypes.c_uint32),("field_address",ctypes.c_uint32),("field_before",ctypes.c_uint32),("field_after",ctypes.c_uint32),("modulus",ctypes.c_uint32),("replacement",ctypes.c_uint32),("service_state_address",ctypes.c_uint32),("service_state_value",ctypes.c_uint32)] + ([ ("secondary_clear_address",ctypes.c_uint32) ] if name == "b" else []) + [("return_target",ctypes.c_uint32)]
 return R
def main():
 with tempfile.TemporaryDirectory(prefix="von-input-arms-") as d:
  so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_bookkeeping_input_a_arm_f2c20.c"),str(ROOT/"von/i960/recovered_diagnostic_bookkeeping_input_b_arm_f2c90.c")],check=True)
  lib=ctypes.CDLL(str(so)); A=build("a"); B=build("b"); a=lib.recovered_diagnostic_bookkeeping_input_a_arm_f2c20;b=lib.recovered_diagnostic_bookkeeping_input_b_arm_f2c90;a.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(A)];b.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(B)];ao=A();bo=B();a(1,9,ctypes.byref(ao));b(1,0,ctypes.byref(bo));assert (ao.field_after,ao.pattern_address,ao.return_target)==(1,0x1004514,0xf2c84);assert (bo.field_after,bo.secondary_clear_address,bo.return_target)==(2,0x1004514,0xf2cfc);print("PASS: 0xf2c20/0xf2c90 bookkeeping input arms")
if __name__=="__main__":main()
