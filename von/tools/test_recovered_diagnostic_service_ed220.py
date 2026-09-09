#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure): _fields_=[(n,ctypes.c_uint32) for n in ("result_state_before","result_state_initialized","reset_performed","reset_call","initial_format_call","initial_format_x","initial_format_y","prompt_string_address","prompt_renderer","menu_renderer","event_mode_flag","dispatch_counter","dispatch_handler_address","dispatch_handler_table","dispatch_save_address","fallback_call","fallback_status_value","fallback_save_address","status_counter_address","return_target")]
def main():
    with tempfile.TemporaryDirectory(prefix="von-diagnostic-service-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_service_ed220.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_service_ed220; fn.argtypes=[ctypes.c_uint32]*4; fn.restype=Result
        out=fn(0,0,8,0); assert (out.reset_call,out.initial_format_call,out.initial_format_x,out.initial_format_y,out.prompt_string_address,out.prompt_renderer,out.menu_renderer,out.dispatch_handler_address,out.return_target)==(0xed0d0,0xeaf20,18,6,0xed200,0xf5100,0xecd80,0xec920,0xed2e0)
        out=fn(1,0,8,0); assert (out.result_state_initialized,out.reset_performed,out.dispatch_handler_address,out.return_target)==(0,0,0xec920,0xed2e0)
        out=fn(1,1,8,1); assert (out.prompt_string_address,out.dispatch_handler_address,out.fallback_call,out.fallback_status_value,out.return_target)==(0xed1e0,0xec920,0xeade8,2,0xed300)
        print("PASS: 0xed220 diagnostic service")
if __name__=="__main__": main()
