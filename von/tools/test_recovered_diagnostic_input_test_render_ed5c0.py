#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[("header_x",ctypes.c_uint32),("header_y",ctypes.c_uint32),("header_string",ctypes.c_uint32),("base_row_count",ctypes.c_uint32),("base_row_x",ctypes.c_uint32*12),("base_row_y",ctypes.c_uint32*12),("base_row_string",ctypes.c_uint32*12),("conditional_row_count",ctypes.c_uint32),("conditional_flag_bit",ctypes.c_uint32*12),("conditional_row_x",ctypes.c_uint32*12),("conditional_row_y",ctypes.c_uint32*12),("conditional_string",ctypes.c_uint32),("prompt_x",ctypes.c_uint32),("prompt_y",ctypes.c_uint32),("prompt_string",ctypes.c_uint32),("input_wrapper",ctypes.c_uint32),("renderer",ctypes.c_uint32),("flag_address",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-input-render-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_input_test_render_ed5c0.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_input_test_render_ed5c0; fn.restype=Result; out=fn()
        assert (out.header_x,out.header_y,out.header_string,out.base_row_count,out.conditional_row_count,out.conditional_string,out.prompt_x,out.prompt_y,out.prompt_string,out.input_wrapper,out.renderer,out.flag_address,out.return_target)==(21,6,0xeaf70,12,12,0xed5b4,20,39,0xed1e0,0xeaeb0,0xf5100,0x50249c,0xed968)
        assert list(out.base_row_y)==[11,13,15,17,19,21,23,27,30,32,34,36]; assert list(out.conditional_flag_bit)==[13,12,14,15,8,9,21,20,22,23,16,17]; assert list(out.conditional_row_x)==[34]*6+[39]*6
        print("PASS: 0xed5c0 input-test renderer layout")
if __name__=="__main__": main()
