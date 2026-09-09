#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[("result_state_before",ctypes.c_uint32),("result_state_after",ctypes.c_uint32),("initialized",ctypes.c_uint32),("branch_address",ctypes.c_uint32),("branch_value",ctypes.c_uint32),("probe_result",ctypes.c_uint32),("counter_address",ctypes.c_uint32),("counter_before",ctypes.c_uint32),("counter_after",ctypes.c_uint32),("counter_modulus",ctypes.c_uint32),("table_address",ctypes.c_uint32),("selected_index",ctypes.c_uint32),("selected_handler",ctypes.c_uint32),("alternate_counter_address",ctypes.c_uint32),("alternate_counter_before",ctypes.c_uint32),("alternate_counter_after",ctypes.c_uint32),("alternate_table_address",ctypes.c_uint32),("alternate_index",ctypes.c_uint32),("alternate_handler",ctypes.c_uint32),("initialization_call",ctypes.c_uint32),("probe_call",ctypes.c_uint32),("handler_call",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-bookkeeping-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_bookkeeping_service_f2e20.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_bookkeeping_service_f2e20; fn.argtypes=[ctypes.c_uint32]*6+[ctypes.POINTER(ctypes.c_uint32)]*2+[ctypes.POINTER(Result)]
        a=(ctypes.c_uint32*5)(0x2940,0x2a60,0x2ae0,0x2b60,0x2bc0); b=(ctypes.c_uint32*5)(0x2940,0x2c20,0x2c90,0x2d00,0x2d70); out=Result(); fn(0,0,1,0,4,2,a,b,ctypes.byref(out)); assert (out.result_state_after,out.counter_after,out.selected_index,out.selected_handler,out.table_address,out.return_target)==(0xffffffff,0,0,0x2940,0xf2de0,0xf2ee4)
        fn(1,1,0,1,4,2,a,b,ctypes.byref(out)); assert (out.alternate_counter_after,out.alternate_index,out.alternate_handler,out.handler_call)==(3,3,0x2d00,0x2d00); print("PASS: 0xf2e20 bookkeeping service")
if __name__=="__main__": main()
