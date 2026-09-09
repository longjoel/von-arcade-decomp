#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[("preparation_call",ctypes.c_uint32*4),("zero_argument",ctypes.c_uint32),("builder_call",ctypes.c_uint32),("status_counter_before",ctypes.c_uint32),("status_counter_after",ctypes.c_uint32),("status_counter_address",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-alt-pipeline-dispatch-") as d:
        so=Path(d)/"dispatch.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_runtime_alt_record_pipeline_dispatch_ec8f0.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_runtime_alt_record_pipeline_dispatch_ec8f0; fn.argtypes=[ctypes.c_uint32]; fn.restype=Result; out=fn(80)
        assert list(out.preparation_call)==[0x29a80,0x1c220,0x1bda0,0x28840]; assert (out.zero_argument,out.builder_call,out.status_counter_after,out.status_counter_address,out.return_target)==(0,0xec820,81,0x578510,0xec91c)
        print("PASS: 0xec8f0 alternate record pipeline dispatcher")
if __name__=="__main__": main()
