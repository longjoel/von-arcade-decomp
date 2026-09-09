#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure): _fields_=[(n,ctypes.c_uint32) for n in ("entry_address","source_base","input_byte_count","checksum_variant","output_address","checksum_continuation","status_counter_before","status_counter_after","status_counter_address","return_target")]
def main():
    with tempfile.TemporaryDirectory(prefix="von-event-publish-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_runtime_event_result_publish_wrappers_eca30.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_runtime_event_result_publish_wrapper; fn.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(Result)]; fn.restype=ctypes.c_int
        expected={0xeca30:(0x2000000,0x800000,4,0x578538,0xec9c0),0xeca60:(0x2000000,0x800000,3,0x57853c,0xeca28),0xeca90:(0x2800000,0x800000,4,0x578530,0xec9c0),0xecac0:(0x2800000,0x800000,3,0x578534,0xeca28),0xecaf0:(0x1000000,0x1000000,4,0x578540,0xec9c0),0xecb20:(0x1000000,0x1000000,3,0x578544,0xeca28)}
        for entry, values in expected.items():
            out=Result(); assert fn(entry,100,ctypes.byref(out))==1; assert (out.source_base,out.input_byte_count,out.checksum_variant,out.output_address,out.checksum_continuation,out.status_counter_after)==(*values,101)
        out=Result(); assert fn(0,100,ctypes.byref(out))==0; print("PASS: 0xeca30-0xecb48 event-result publishers")
if __name__=="__main__": main()
