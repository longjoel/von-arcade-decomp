#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [("result_state_address",ctypes.c_uint32),("result_state_before",ctypes.c_uint32),("result_state_after",ctypes.c_uint32),("initialization_call",ctypes.c_uint32),("initialization_performed",ctypes.c_uint32),("counter_address",ctypes.c_uint32),("counter_value",ctypes.c_uint32),("header_x",ctypes.c_uint32),("header_y",ctypes.c_uint32),("header_string",ctypes.c_uint32),("label_wrapper",ctypes.c_uint32),("mode_state_address",ctypes.c_uint32),("mode_state",ctypes.c_uint32),("prompt_x",ctypes.c_uint32),("prompt_y",ctypes.c_uint32),("prompt_string",ctypes.c_uint32),("builder_count",ctypes.c_uint32),("builder_destination",ctypes.c_uint32*8),("builder_source",ctypes.c_uint32*8),("builder_flags",ctypes.c_uint32*8),("structure_destination",ctypes.c_uint32),("structure_first_value",ctypes.c_uint32),("structure_repeat_value",ctypes.c_uint32),("structure_repeat_count",ctypes.c_uint32),("structure_tail_value",ctypes.c_uint32),("structure_tail_count",ctypes.c_uint32),("fallback_call",ctypes.c_uint32),("state_reset_value",ctypes.c_uint32),("mode_counter_after",ctypes.c_uint32),("pending_state_address",ctypes.c_uint32),("pending_state_value",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-match-time-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_match_time_test_service_f0980.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_match_time_test_service_f0980; fn.argtypes=[ctypes.c_uint32]*4+[ctypes.POINTER(Result)]
        out=Result(); fn(0,0,0,15,ctypes.byref(out)); assert (out.result_state_after,out.header_string,out.prompt_string,out.builder_count,list(out.builder_source)[:2],out.return_target)==(1,0xf0940,0xf0960,2,[0x2bde7ac,0x2be27ec],0xf0b38)
        fn(1,3,0,10,ctypes.byref(out)); assert (out.initialization_performed,out.prompt_string,out.builder_count,list(out.builder_source)[:5],out.structure_repeat_count,out.pending_state_value)==(0,0xed1e0,5,[0x2bde82c,0x2be286c,0x2be28ac,0x2be28ec,0x2be292c],41,2); print("PASS: 0xf0980 match/time diagnostic service")
if __name__=="__main__": main()
