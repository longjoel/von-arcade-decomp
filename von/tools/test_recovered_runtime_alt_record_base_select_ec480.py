#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[(n,ctypes.c_uint32) for n in ("selected_base","selected_family","matched","fallback_counter_before","fallback_counter_after","fallback_counter_address","continuation_address","indirect_return_address")]
def main():
    with tempfile.TemporaryDirectory(prefix="von-alt-base-select-") as d:
        so=Path(d)/"select.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_runtime_alt_record_base_select_ec480.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_runtime_alt_record_base_select_ec480; fn.argtypes=[ctypes.POINTER(ctypes.c_uint32),ctypes.c_uint32]; fn.restype=Result
        for index, base in enumerate((0x200000,0x1000000,0x1080000,0x1800000,0x1810000,0x1814000,0x1818000), 1):
            markers=(ctypes.c_uint32*15)();
            for slot in ((0,1,2,3),(4,5),(6,7,8,9),(10,11),(12,),(13,),(14,))[index-1]: markers[slot]=1
            out=fn(markers,7); assert (out.selected_base,out.selected_family,out.matched,out.fallback_counter_after)==(base,index,1,7)
        markers=(ctypes.c_uint32*15)(); out=fn(markers,7)
        assert (out.selected_base,out.matched,out.fallback_counter_after,out.fallback_counter_address,out.continuation_address,out.indirect_return_address)==(0,0,8,0x578510,0xec5b8,0xec61c)
        print("PASS: 0xec480 alternate record base selector")
if __name__=="__main__": main()
