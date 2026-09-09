#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[(n,ctypes.c_uint32) for n in ("input_byte_count","chunk_count","checksum","first_byte_offset","second_byte_offset","chunk_stride_bytes","continuation_address","return_target")]
def main():
    with tempfile.TemporaryDirectory(prefix="von-record-checksum-") as d:
        so=Path(d)/"checksum.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_runtime_record_checksums_ec970.c")],check=True)
        lib=ctypes.CDLL(str(so)); data=(ctypes.c_uint8*8)(1,2,30,40,5,6,70,80); out=Result()
        for name, offsets, continuation in (("recovered_runtime_record_checksum_4stride_ec970",(0,1),0xec9c0),("recovered_runtime_record_checksum_3stride_ec9d0",(2,3),0xeca28)):
            fn=getattr(lib,name); fn.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.c_uint32,ctypes.POINTER(Result)]; fn.restype=ctypes.c_int
            assert fn(data,8,ctypes.byref(out))==1; assert (out.chunk_count,out.checksum,out.first_byte_offset,out.second_byte_offset,out.chunk_stride_bytes,out.continuation_address,out.return_target)==(2,sum(data[i*4+offsets[0]]+data[i*4+offsets[1]] for i in range(2)),*offsets,4,continuation,continuation)
            assert fn(data,6,ctypes.byref(out))==0
        print("PASS: 0xec970/0xec9d0 record checksums")
if __name__=="__main__": main()
