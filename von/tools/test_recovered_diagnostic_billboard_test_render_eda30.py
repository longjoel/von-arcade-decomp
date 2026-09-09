#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[("header_x",ctypes.c_uint32),("header_y",ctypes.c_uint32),("header_string",ctypes.c_uint32),("pattern_helper",ctypes.c_uint32),("pattern_count",ctypes.c_uint32),("pattern_value",ctypes.c_uint32*6),("state_address",ctypes.c_uint32),("hardware_flag_address",ctypes.c_uint32),("modulo_address",ctypes.c_uint32),("winner_x",ctypes.c_uint32),("winner_y",ctypes.c_uint32),("winner_p1_string",ctypes.c_uint32),("winner_p2_string",ctypes.c_uint32),("seven_segment_x",ctypes.c_uint32),("seven_segment_y",ctypes.c_uint32),("seven_segment_p1_string",ctypes.c_uint32),("start_lamp_x",ctypes.c_uint32),("start_lamp_y",ctypes.c_uint32),("start_lamp_string",ctypes.c_uint32),("status_word_address",ctypes.c_uint32),("wrapper_address",ctypes.c_uint32),("fallback_call",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-billboard-render-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_billboard_test_render_eda30.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_billboard_test_render_eda30; fn.restype=Result; out=fn()
        assert (out.header_x,out.header_y,out.header_string,out.pattern_helper,out.pattern_count,out.state_address,out.hardware_flag_address,out.modulo_address,out.winner_x,out.winner_y,out.winner_p1_string,out.winner_p2_string,out.status_word_address,out.wrapper_address,out.fallback_call,out.return_target)==(21,6,0xeaf80,0x184e8,6,0x5785c4,0x503a08,0x5024e8,16,18,0xed9b0,0xed9c0,0x502484,0xeaeb0,0xeade8,0xedcf8)
        assert list(out.pattern_value)==[0x1f,0x3f,0x5f,0x7f,0x97,0x9f]
        print("PASS: 0xeda30 billboard test layout")
if __name__=="__main__": main()
