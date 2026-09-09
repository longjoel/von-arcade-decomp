#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure): _fields_=[(n,ctypes.c_uint32) for n in ("state_before","state_after","result_state_initialized","initial_format_call","initial_format_x","initial_format_y","hardware_word_a","hardware_word_b","combined_status","external_service_call","input_format_call","input_format_x","input_format_y","input_format_string","fallback_call","fallback_status_value","final_wrapper_call","final_wrapper_x","final_wrapper_y","final_wrapper_string","fallback_save_address","return_target")]
def main():
    with tempfile.TemporaryDirectory(prefix="von-input-test-service-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_input_test_service_ed320.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_input_test_service_ed320; fn.argtypes=[ctypes.c_uint32]*4; fn.restype=Result
        out=fn(1,0,0,0); assert (out.state_after,out.initial_format_call,out.initial_format_x,out.initial_format_y,out.return_target)==(2,0xeaf20,23,6,0xed438)
        out=fn(2,0x4,1,0); assert (out.state_after,out.combined_status,out.input_format_call,out.input_format_x,out.input_format_y,out.input_format_string,out.fallback_call,out.fallback_status_value)==(3,3,0x1cac8,24,17,0xed308,0xeade8,0)
        out=fn(0,0,0,0); assert (out.state_after,out.input_format_call,out.final_wrapper_call,out.final_wrapper_x,out.final_wrapper_y,out.final_wrapper_string,out.fallback_call)==(0,0,0xeaeb0,20,39,0xed1e0,0xeade8)
        out=fn(3,0,0,1); assert (out.state_after,out.external_service_call,out.return_target)==(4,0x29330,0xed438)
        print("PASS: 0xed320 diagnostic input-test service")
if __name__=="__main__": main()
