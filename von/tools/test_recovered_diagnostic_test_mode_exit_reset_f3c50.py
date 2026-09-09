#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
 _fields_=[("result_state_address",ctypes.c_uint32),("result_state_before",ctypes.c_uint32),("result_state_after",ctypes.c_uint32),("initialization_performed",ctypes.c_uint32),("initialization_call",ctypes.c_uint32),("exit_marker_address",ctypes.c_uint32),("exit_marker_value",ctypes.c_uint32),("frequency_address",ctypes.c_uint32),("frequency_before",ctypes.c_uint32),("frequency_after",ctypes.c_uint32),("transient_byte_address",ctypes.c_uint32),("transient_word_address",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
 with tempfile.TemporaryDirectory(prefix="von-test-mode-exit-") as d:
  so=Path(d)/"x.so";subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_test_mode_exit_reset_f3c50.c")],check=True);fn=ctypes.CDLL(str(so)).recovered_diagnostic_test_mode_exit_reset_f3c50;fn.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(Result)];out=Result();fn(0,41,ctypes.byref(out));assert (out.result_state_after,out.exit_marker_value,out.frequency_after,out.transient_byte_address,out.transient_word_address,out.return_target)==(1,0x52,42,0x5770b0,0x503a00,0xf3c9c);fn(1,41,ctypes.byref(out));assert out.initialization_performed==0;print("PASS: 0xf3c50 test-mode exit/reset")
if __name__=="__main__":main()
