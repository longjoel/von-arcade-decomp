#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[("settings_renderer",ctypes.c_uint32),("pattern_address",ctypes.c_uint32),("pattern_value",ctypes.c_uint32),("clear_address",ctypes.c_uint32),("probe_call",ctypes.c_uint32),("probe_result",ctypes.c_uint32),("setting_address",ctypes.c_uint32),("setting_before",ctypes.c_uint32),("setting_after",ctypes.c_uint32),("modulus",ctypes.c_uint32),("zero_replacement",ctypes.c_uint32),("configuration_decoder",ctypes.c_uint32),("bookkeeping_mode_address",ctypes.c_uint32),("bookkeeping_mode_value",ctypes.c_uint32),("service_state_address",ctypes.c_uint32),("service_state_value",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-manual-setting-arm-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_bookkeeping_manual_setting_arm_f2b60.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_bookkeeping_manual_setting_arm_f2b60; fn.argtypes=[ctypes.c_uint32]*2+[ctypes.POINTER(Result)]
        out=Result(); fn(1,27,ctypes.byref(out)); assert (out.setting_after,out.modulus,out.configuration_decoder,out.bookkeeping_mode_value,out.return_target)==(1,28,0xf19e8,1,0xf2bbc)
        fn(0,4,ctypes.byref(out)); assert out.setting_after==4; print("PASS: 0xf2b60 bookkeeping manual-setting arm")
if __name__=="__main__": main()
