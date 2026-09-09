#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure): _fields_=[(n,ctypes.c_uint32) for n in ("destination_base","plane_count","rows_per_plane","halfwords_per_row","plane","row","halfword","destination_address","pattern_value","return_target")]
def main():
    with tempfile.TemporaryDirectory(prefix="von-crt-buffer-fill-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_crt_pattern_buffer_fill_f08c0.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_diagnostic_crt_pattern_buffer_fill_f08c0; fn.argtypes=[ctypes.c_uint32]*3+[ctypes.POINTER(Result)]; fn.restype=ctypes.c_int
        for args in ((0,0,0),(3,5,31),(2,4,17)):
            out=Result(); assert fn(*args,ctypes.byref(out))==1; plane,row,halfword=args
            assert (out.destination_base,out.plane_count,out.rows_per_plane,out.halfwords_per_row,out.destination_address,out.pattern_value,out.return_target)==(0x100461e,4,6,32,0x100461e+((row+plane*6)<<7)+(halfword<<1),0x2000+((plane*4+(halfword>>3))<<7)+(halfword&7),0xf0938)
        out=Result(); assert fn(4,0,0,ctypes.byref(out))==0; print("PASS: 0xf08c0 CRT pattern buffer fill")
if __name__=="__main__": main()
