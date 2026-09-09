#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[("status_address",ctypes.c_uint32),("status_word",ctypes.c_uint32),("input_x",ctypes.c_uint32),("input_y",ctypes.c_uint32),("first_x",ctypes.c_uint32),("first_y",ctypes.c_uint32),("second_x",ctypes.c_uint32),("second_y",ctypes.c_uint32),("early_return",ctypes.c_uint32),("type27_special",ctypes.c_uint32),("first_table_index",ctypes.c_uint32),("second_table_index",ctypes.c_uint32),("table_address",ctypes.c_uint32),("first_value_a",ctypes.c_uint32),("first_value_b",ctypes.c_uint32),("first_value_c",ctypes.c_uint32),("second_value_a",ctypes.c_uint32),("second_value_b",ctypes.c_uint32),("second_value_c",ctypes.c_uint32),("first_formatter",ctypes.c_uint32),("second_formatter",ctypes.c_uint32),("label_wrapper",ctypes.c_uint32),("type_string",ctypes.c_uint32),("free_play_string",ctypes.c_uint32),("blank_string",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-chute-status-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_coin_chute_status_render_f1f20.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_coin_chute_status_render_f1f20; fn.argtypes=[ctypes.c_uint32]*3+[ctypes.POINTER(Result)]
        out=Result(); fn(27,40,10,ctypes.byref(out)); assert (out.type27_special,out.first_table_index,out.first_formatter,out.free_play_string,out.second_y,out.return_target)==(1,108,0,0xf1ee0,16,0xf20a4)
        fn(5,40,10,ctypes.byref(out)); assert (out.early_return,out.first_table_index,out.first_value_a,out.first_value_b,out.first_value_c,out.second_value_b,out.second_formatter)==(0,20,0xead44,0xead46,0xead47,0xead45,0xf1db0); print("PASS: 0xf1f20 coin-chute status renderer")
if __name__=="__main__": main()
