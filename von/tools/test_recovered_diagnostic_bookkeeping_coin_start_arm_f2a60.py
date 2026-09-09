#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[("settings_renderer",ctypes.c_uint32),("pattern_address",ctypes.c_uint32),("pattern_value",ctypes.c_uint32),("clear_address",ctypes.c_uint32),("probe_call",ctypes.c_uint32),("probe_result",ctypes.c_uint32),("coin_address",ctypes.c_uint32),("coin_before",ctypes.c_uint32),("coin_after",ctypes.c_uint32),("credit_address",ctypes.c_uint32),("credit_before",ctypes.c_uint32),("credit_after",ctypes.c_uint32),("modulus",ctypes.c_uint32),("service_state_address",ctypes.c_uint32),("service_state_value",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-coin-start-arm-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_bookkeeping_coin_start_arm_f2a60.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_bookkeeping_coin_start_arm_f2a60; fn.argtypes=[ctypes.c_uint32]*3+[ctypes.POINTER(Result)]
        out=Result(); fn(1,4,4,ctypes.byref(out)); assert (out.coin_after,out.credit_after,out.pattern_address,out.clear_address,out.return_target)==(0,0,0x1004622,0x10050a2,0xf2ad8)
        fn(1,1,4,ctypes.byref(out)); assert out.credit_after==0; print("PASS: 0xf2a60 bookkeeping coin-start arm")
if __name__=="__main__": main()
