#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[("input_gate_result",ctypes.c_uint32),("early_return",ctypes.c_uint32),("mode_address",ctypes.c_uint32),("mode_value",ctypes.c_uint32),("result_state_address",ctypes.c_uint32),("result_state_value",ctypes.c_uint32),("probe_call",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-site-fallback-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_site_status_fallback_f1bc0.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_site_status_fallback_f1bc0; fn.argtypes=[ctypes.c_uint32,ctypes.POINTER(Result)]
        out=Result(); fn(0,ctypes.byref(out)); assert out.early_return==1
        fn(1,ctypes.byref(out)); assert (out.mode_address,out.mode_value,out.result_state_address,out.result_state_value,out.probe_call,out.return_target)==(0x5784f8,2,0x578500,0,0xeade8,0xf1bdc); print("PASS: 0xf1bc0 site/status fallback")
if __name__=="__main__": main()
