#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_=[(n,ctypes.c_uint32) for n in ("source_pointer_address","source_pointer","destination_base","copied_halfword_count","loop_terminal_value","status_counter_before","status_counter_after","status_counter_address","continuation_address","indirect_return_address")]
def main():
    with tempfile.TemporaryDirectory(prefix="von-alt-table-copy-") as d:
        so=Path(d)/"copy.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_runtime_alt_record_table_copy_ec630.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_runtime_alt_record_table_copy_ec630; fn.argtypes=[ctypes.c_uint32,ctypes.c_uint32]; fn.restype=Result; out=fn(0x1818000,60)
        assert (out.source_pointer_address,out.source_pointer,out.destination_base,out.copied_halfword_count,out.loop_terminal_value,out.status_counter_after,out.status_counter_address,out.continuation_address,out.indirect_return_address)==(0x5785ac,0x1818000,0x1d00000,0x2000,0x1fff,61,0x578510,0xec698,0xec694)
        print("PASS: 0xec630 alternate record-table copy")
if __name__=="__main__": main()
