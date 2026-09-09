#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[("divisor_r8",ctypes.c_uint32),("addend_r11",ctypes.c_uint32),("scale_r12",ctypes.c_uint32),("x_base_r10",ctypes.c_uint32),("y_base_r9",ctypes.c_uint32),("valid",ctypes.c_uint32),("iteration_count",ctypes.c_uint32),("rendered_count",ctypes.c_uint32),("product",ctypes.c_uint32*5),("adjusted_product",ctypes.c_uint32*5),("quotient",ctypes.c_uint32*5),("remainder",ctypes.c_uint32*5),("render_kind",ctypes.c_uint32*5),("rendered_string",ctypes.c_uint32*5),("rendered_x",ctypes.c_uint32*5),("rendered_y",ctypes.c_uint32*5),("blank_string",ctypes.c_uint32),("special_string",ctypes.c_uint32),("general_string",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-credit-math-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_credit_math_formatter_f1db0.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_credit_math_formatter_f1db0; fn.argtypes=[ctypes.c_uint32]*5+[ctypes.POINTER(Result)]
        out=Result(); assert fn(10,20,3,1,10,ctypes.byref(out))==1; assert (list(out.product),list(out.adjusted_product),list(out.quotient),list(out.render_kind),list(out.rendered_string),out.return_target)==([1,2,3,4,5],[1,2,3,4,5],[0,0,1,1,1],[0,0,2,0,0],[0xf1d90,0xf1d90,0xf1d70,0xf1d90,0xf1d90],0xf1ebc)
        assert fn(0,0,0,1,1,ctypes.byref(out))==0 and out.valid==0; print("PASS: 0xf1db0 credit arithmetic formatter")
if __name__=="__main__": main()
