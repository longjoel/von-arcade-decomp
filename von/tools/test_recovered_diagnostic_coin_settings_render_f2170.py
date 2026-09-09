#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[("title_x",ctypes.c_uint32),("title_y",ctypes.c_uint32),("title_string",ctypes.c_uint32),("title_renderer",ctypes.c_uint32),("coin_start_address",ctypes.c_uint32),("coin_start_value",ctypes.c_uint32),("coin_start_string",ctypes.c_uint32),("credit_start_address",ctypes.c_uint32),("credit_start_value",ctypes.c_uint32),("credit_start_string",ctypes.c_uint32),("manual_setting_address",ctypes.c_uint32),("manual_setting_value",ctypes.c_uint32),("manual_setting_string",ctypes.c_uint32),("manual_setting_special",ctypes.c_uint32),("status_renderer",ctypes.c_uint32),("label_wrapper",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-coin-settings-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_coin_settings_render_f2170.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_coin_settings_render_f2170; fn.argtypes=[ctypes.c_uint32]*3+[ctypes.POINTER(Result)]
        out=Result(); fn(0,3,0,ctypes.byref(out)); assert (out.title_x,out.title_y,out.coin_start_string,out.credit_start_string,out.manual_setting_special,out.manual_setting_string,out.status_renderer,out.return_target)==(18,6,0xf20f0,0xf2100,1,0xf2150,0xf1f20,0xf22e0)
        fn(2,0,27,ctypes.byref(out)); assert (out.coin_start_string,out.credit_start_string,out.manual_setting_special,out.manual_setting_string)==(0xf2100,0xf20f0,0,0xf2160); print("PASS: 0xf2170 coin settings renderer")
if __name__=="__main__": main()
