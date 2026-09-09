#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure): _fields_=[("table_address",ctypes.c_uint32),("entry_count",ctypes.c_uint32),("handler",ctypes.c_uint32*11),("return_boundary",ctypes.c_uint32)]
def main():
 with tempfile.TemporaryDirectory(prefix="von-diagnostic-table-") as d:
  so=Path(d)/"x.so";subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_service_handler_table_f3ec0.c")],check=True);fn=ctypes.CDLL(str(so)).recovered_diagnostic_service_handler_table_f3ec0;fn.restype=Result;r=fn();assert (r.table_address,r.entry_count,list(r.handler),r.return_boundary)==(0xf3ec0,11,[0xed220,0xed320,0xed5c0,0xeda30,0xf04d0,0xf0980,0xf1c90,0xf2e20,0xf33a0,0xf3ab0,0xf3c50],0xf3ee8);print("PASS: 0xf3ec0 diagnostic service handler table")
if __name__=="__main__":main()
