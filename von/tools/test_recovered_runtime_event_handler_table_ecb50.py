#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure): _fields_=[("base_address",ctypes.c_uint32),("entry_count",ctypes.c_uint32),("entry",ctypes.c_uint32*25),("terminator_address",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-event-handler-table-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_runtime_event_handler_table_ecb50.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_runtime_event_handler_table_ecb50; fn.restype=Result; out=fn()
        assert (out.base_address,out.entry_count,out.terminator_address)==(0xecb50,25,0xecbb4)
        assert list(out.entry)==[0xeca30,0xeca60,0xeca90,0xecac0,0xecaf0,0xecb20,0xeb2c0,0xebab0,0xec920,0xebe20,0xebc60,0xebfd0,0xec140,0xec290,0xec3e0,0xec8f0,0xec480,0xec760,0xec630,0xeb830,0xec8f0,0xec940,0xec940,0xec940,0xec940]
        print("PASS: 0xecb50 event-handler table")
if __name__=="__main__": main()
