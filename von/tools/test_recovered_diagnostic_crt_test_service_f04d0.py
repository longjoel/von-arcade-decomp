#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure): _fields_=[("result_state_address",ctypes.c_uint32),("result_state_init_value",ctypes.c_uint32),("pattern_state_address",ctypes.c_uint32),("pattern_state_init_value",ctypes.c_uint32),("pattern_state_initial",ctypes.c_uint32),("pattern_data_address",ctypes.c_uint32),("pattern_data_init_value",ctypes.c_uint32),("continuation_address",ctypes.c_uint32),("header_x",ctypes.c_uint32),("header_y",ctypes.c_uint32),("header_string",ctypes.c_uint32),("label_wrapper",ctypes.c_uint32),("pattern_service",ctypes.c_uint32),("handler_table_address",ctypes.c_uint32),("handler_count",ctypes.c_uint32),("handler_address",ctypes.c_uint32*6),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-crt-service-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_crt_test_service_f04d0.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_crt_test_service_f04d0; fn.restype=Result; out=fn()
        assert (out.result_state_address,out.result_state_init_value,out.pattern_state_address,out.pattern_state_initial,out.pattern_data_address,out.pattern_data_init_value,out.header_x,out.header_y,out.header_string,out.label_wrapper,out.pattern_service,out.handler_table_address,out.handler_count,out.return_target)==(0x578500,1,0x5784f4,6,0x1004e14,30,12,6,0xeaf90,0xeaeb0,0x184e8,0xf0674,6,0xf08b4)
        assert list(out.handler_address)==[0xf068c,0xf06ec,0xf074c,0xf07b8,0xf0818,0xf0888]; print("PASS: 0xf04d0 CRT diagnostic service")
if __name__=="__main__": main()
