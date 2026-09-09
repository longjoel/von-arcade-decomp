#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[("source_status_address",ctypes.c_uint32),("source_status_word",ctypes.c_uint32),("packed_index",ctypes.c_uint32),("table_address",ctypes.c_uint32),("lookup_address",ctypes.c_uint32*4),("lookup_value",ctypes.c_uint32*4),("output_address",ctypes.c_uint32*4),("output_value",ctypes.c_uint32*4),("normalized_status",ctypes.c_uint32),("normalized_status_address",ctypes.c_uint32),("service_state_address",ctypes.c_uint32),("service_state_value",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-config-decode-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_coin_configuration_decode_f19e8.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_coin_configuration_decode_f19e8; fn.argtypes=[ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(Result)]
        values=(ctypes.c_uint32*4)(7,8,9,1); out=Result(); fn(5,values,ctypes.byref(out)); assert (out.packed_index,list(out.lookup_address),list(out.output_address),out.normalized_status,out.service_state_value,out.return_target)==(20,[0xead44,0xead46,0xead45,0xead47],[0x1d00035,0x1d00030,0x1d00032,0x1d00036],1,1,0xf1aa8)
        values[3]=2; fn(5,values,ctypes.byref(out)); assert out.normalized_status==0; print("PASS: 0xf19e8 coin configuration decoder")
if __name__=="__main__": main()
