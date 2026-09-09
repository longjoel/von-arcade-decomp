#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[(n,ctypes.c_uint32) for n in ("packed_byte_count","initialized_halfword_count","scan_record_count","target_word","scan_base","match_59c","match_5a0","slot_59c_address","slot_5a0_address","return_target")]
def main():
    with tempfile.TemporaryDirectory(prefix="von-alt-packed-scan-g-") as d:
        so=Path(d)/"scan.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_runtime_alt_packed_record_scan_g_ec6a0.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_runtime_alt_packed_record_scan_g_ec6a0; fn.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint16),ctypes.c_uint32,ctypes.POINTER(Result)]; fn.restype=ctypes.c_int
        words=(ctypes.c_uint16*6)(0x0034,0x5600,0x1200,0x0034,0,0); out=Result(); assert fn(6,0x1234,words,6,ctypes.byref(out))==1
        assert (out.scan_record_count,out.scan_base,out.match_59c,out.match_5a0,out.slot_59c_address,out.slot_5a0_address,out.return_target)==(3,0x5785aa,0x5785ae,0x5785b0,0x57859c,0x5785a0,0xec75c)
        assert fn(6,0x1234,words,5,ctypes.byref(out))==0; print("PASS: 0xec6a0 final paired alternate packed-record scan")
if __name__=="__main__": main()
