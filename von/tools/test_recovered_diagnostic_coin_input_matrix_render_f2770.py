#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[("title_x",ctypes.c_uint32),("title_y",ctypes.c_uint32),("title_string",ctypes.c_uint32),("title_renderer",ctypes.c_uint32),("matrix_builder",ctypes.c_uint32),("first_x",ctypes.c_uint32),("first_y_address",ctypes.c_uint32),("first_y_value",ctypes.c_uint32),("second_x",ctypes.c_uint32),("second_y_address",ctypes.c_uint32),("second_y_value",ctypes.c_uint32),("first_mode_address",ctypes.c_uint32),("first_mode_value",ctypes.c_uint32),("first_string",ctypes.c_uint32),("second_mode_address",ctypes.c_uint32),("second_mode_value",ctypes.c_uint32),("second_string",ctypes.c_uint32),("first_zero_string",ctypes.c_uint32),("first_value_string",ctypes.c_uint32),("second_zero_string",ctypes.c_uint32),("second_value_string",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-coin-matrix-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_coin_input_matrix_render_f2770.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_coin_input_matrix_render_f2770; fn.argtypes=[ctypes.c_uint32]*4+[ctypes.POINTER(Result)]
        out=Result(); fn(1,0,4,5,ctypes.byref(out)); assert (out.title_x,out.matrix_builder,out.first_x,out.first_y_address,out.second_x,out.first_string,out.second_string,out.return_target)==(18,0xf23e0,17,0x1d00030,27,0xf2670,0xf26d0,0xf2930)
        fn(2,1,4,5,ctypes.byref(out)); assert (out.first_string,out.second_string)==(0xf2690,0xf26f0); print("PASS: 0xf2770 coin/input matrix renderer")
if __name__=="__main__": main()
