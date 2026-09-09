#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
 _fields_=[("settings_renderer",ctypes.c_uint32),("pattern_address",ctypes.c_uint32),("pattern_value",ctypes.c_uint32),("clear_address",ctypes.c_uint32),("probe_call",ctypes.c_uint32),("probe_result",ctypes.c_uint32),("reset_call",ctypes.c_uint32),("selector_address",ctypes.c_uint32),("selector_before",ctypes.c_uint32),("selector_after",ctypes.c_uint32),("type27_value",ctypes.c_uint32),("configuration_decoder",ctypes.c_uint32),("bookkeeping_mode_address",ctypes.c_uint32),("bookkeeping_mode_value",ctypes.c_uint32),("service_state_address",ctypes.c_uint32),("service_state_value",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
 with tempfile.TemporaryDirectory(prefix="von-credit-reset-arm-") as d:
  so=Path(d)/"x.so";subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_bookkeeping_credit_reset_arm_f2bc0.c")],check=True)
  fn=ctypes.CDLL(str(so)).recovered_diagnostic_bookkeeping_credit_reset_arm_f2bc0;fn.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(Result)];out=Result();fn(1,27,ctypes.byref(out));assert (out.selector_after,out.configuration_decoder,out.bookkeeping_mode_value,out.return_target)==(1,0xf19e8,1,0xf2c14);fn(0,27,ctypes.byref(out));assert out.selector_after==27;print("PASS: 0xf2bc0 bookkeeping credit-reset arm")
if __name__=="__main__":main()
