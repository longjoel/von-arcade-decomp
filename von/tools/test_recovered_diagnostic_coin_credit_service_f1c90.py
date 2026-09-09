#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[("result_state_address",ctypes.c_uint32),("result_state_before",ctypes.c_uint32),("result_state_after",ctypes.c_uint32),("initialization_call",ctypes.c_uint32),("initialization_performed",ctypes.c_uint32),("dispatch_result",ctypes.c_uint32),("index_address",ctypes.c_uint32),("index_before",ctypes.c_uint32),("index_after",ctypes.c_uint32),("index_modulus",ctypes.c_uint32),("table_address",ctypes.c_uint32),("table_entry_count",ctypes.c_uint32),("table_handler",ctypes.c_uint32*20),("table_selector",ctypes.c_uint32*20),("pattern_base",ctypes.c_uint32),("pattern_stride",ctypes.c_uint32),("pattern_index",ctypes.c_uint32),("pattern_destination",ctypes.c_uint32),("pattern_value",ctypes.c_uint32),("formatter_call",ctypes.c_uint32),("selected_handler_call",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-coin-credit-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_coin_credit_service_f1c90.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_coin_credit_service_f1c90; fn.argtypes=[ctypes.c_uint32]*3+[ctypes.POINTER(Result)]
        out=Result(); fn(0,1,19,ctypes.byref(out)); assert (out.result_state_after,out.index_after,out.table_entry_count,out.table_handler[0],out.table_handler[19],out.selected_handler_call,out.pattern_destination,out.return_target)==(0xffffffff,0,20,0xf1bc0,0xf1ac0,0xf1bc0,0x100549c,0xf1d40)
        fn(0xffffffff,0,4,ctypes.byref(out)); assert (out.initialization_performed,out.index_after,out.selected_handler_call)==(0,4,0); print("PASS: 0xf1c90 coin/credit diagnostic service")
if __name__=="__main__": main()
