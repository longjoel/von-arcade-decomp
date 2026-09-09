#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[("input_gate_result",ctypes.c_uint32),("early_return",ctypes.c_uint32),("first_source",ctypes.c_uint32),("first_compare_word",ctypes.c_uint32),("first_compare_mask",ctypes.c_uint32),("second_source",ctypes.c_uint32),("second_compare_word",ctypes.c_uint32),("second_compare_mask",ctypes.c_uint32),("first_validation_call",ctypes.c_uint32),("second_validation_call",ctypes.c_uint32),("first_validation_result",ctypes.c_uint32),("second_validation_result",ctypes.c_uint32),("first_status_source",ctypes.c_uint32),("second_status_source",ctypes.c_uint32),("published_status",ctypes.c_uint32),("published_status_address",ctypes.c_uint32),("service_state_address",ctypes.c_uint32),("service_state_value",ctypes.c_uint32),("scratch_call",ctypes.c_uint32),("scratch_length",ctypes.c_uint32),("scratch_table",ctypes.c_uint32),("failure_status",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-site-status-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_site_status_sync_f1ac0.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_site_status_sync_f1ac0; fn.argtypes=[ctypes.c_uint32]*5+[ctypes.POINTER(Result)]
        out=Result(); fn(0,0,0,7,8,ctypes.byref(out)); assert (out.early_return,out.published_status)==(1,0)
        fn(1,0,1,7,8,ctypes.byref(out)); assert (out.published_status,out.published_status_address,out.service_state_value)==(7,0x1d00028,1)
        fn(1,1,1,7,8,ctypes.byref(out)); assert out.published_status==2; print("PASS: 0xf1ac0 site/status synchronizer")
if __name__=="__main__": main()
