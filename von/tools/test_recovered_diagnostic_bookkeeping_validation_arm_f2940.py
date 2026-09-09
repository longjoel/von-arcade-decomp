#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
 _fields_=[("mode_value",ctypes.c_uint32),("settings_renderer",ctypes.c_uint32),("matrix_renderer",ctypes.c_uint32),("probe_call",ctypes.c_uint32),("probe_result",ctypes.c_uint32),("result_state_before",ctypes.c_uint32),("table_address",ctypes.c_uint32),("table_start_offset",ctypes.c_uint32),("record_count",ctypes.c_uint32),("matched",ctypes.c_uint32),("matched_selector",ctypes.c_uint32),("decoded",ctypes.c_uint32*4),("matched_record",ctypes.c_uint32*4),("selector_address",ctypes.c_uint32),("selector_value",ctypes.c_uint32),("result_state_address",ctypes.c_uint32),("result_state_value",ctypes.c_uint32),("mode_address",ctypes.c_uint32),("mode_value_after",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
 with tempfile.TemporaryDirectory(prefix="von-bookkeeping-validate-") as d:
  so=Path(d)/"x.so";subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_bookkeeping_validation_arm_f2940.c")],check=True);lib=ctypes.CDLL(str(so));fn=lib.recovered_diagnostic_bookkeeping_validation_arm_f2940;R=ctypes.c_uint32*4;Rows=(ctypes.c_uint32*4)*25;fn.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(R),ctypes.POINTER(Rows),ctypes.POINTER(Result)];decoded=R(7,8,9,10);rows=Rows();rows[3]=R(7,10,9,8);out=Result();fn(0,1,99,decoded,rows,ctypes.byref(out));assert (out.settings_renderer,out.matched,out.matched_selector,out.selector_value,out.result_state_value,out.return_target)==(0xf2170,1,4,4,99,0xf2a50);fn(1,1,99,decoded,Rows(),ctypes.byref(out));assert (out.matrix_renderer,out.matched,out.result_state_value)==(0xf2770,0,0);print("PASS: 0xf2940 bookkeeping validation arm")
if __name__=="__main__":main()
