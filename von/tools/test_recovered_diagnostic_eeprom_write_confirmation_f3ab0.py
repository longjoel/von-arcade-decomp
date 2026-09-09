#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
 _fields_=[("mode_address",ctypes.c_uint32),("mode_value",ctypes.c_uint32),("result_state_address",ctypes.c_uint32),("result_state_before",ctypes.c_uint32),("result_state_after",ctypes.c_uint32),("activated",ctypes.c_uint32),("initialization_call",ctypes.c_uint32),("pending_address",ctypes.c_uint32),("pending_before",ctypes.c_uint32),("pending_after",ctypes.c_uint32),("first_probe_result",ctypes.c_uint32),("second_probe_result",ctypes.c_uint32),("pattern_value",ctypes.c_uint32),("pattern_a",ctypes.c_uint32),("pattern_b",ctypes.c_uint32),("hardware_clear_a",ctypes.c_uint32),("hardware_clear_b",ctypes.c_uint32),("hardware_clear_c",ctypes.c_uint32),("completion_call",ctypes.c_uint32),("completion_string",ctypes.c_uint32),("completion_x",ctypes.c_uint32),("completion_y",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
 with tempfile.TemporaryDirectory(prefix="von-eeprom-confirm-") as d:
  so=Path(d)/"x.so";subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_eeprom_write_confirmation_f3ab0.c")],check=True);fn=ctypes.CDLL(str(so)).recovered_diagnostic_eeprom_write_confirmation_f3ab0;fn.argtypes=[ctypes.c_uint32]*5+[ctypes.POINTER(Result)];out=Result();fn(1,0,1,1,1,ctypes.byref(out));assert (out.activated,out.result_state_after,out.pending_after,out.completion_call,out.completion_string,out.return_target)==(1,1,1,0x2350,0xf3aa0,0xf3c0c);fn(2,0,1,1,1,ctypes.byref(out));assert out.activated==0;print("PASS: 0xf3ab0 EEPROM confirmation service")
if __name__=="__main__":main()
