#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure): _fields_=[(n,ctypes.c_uint32) for n in ("continuation_address","flag_address","flag_value","return_target")]
def main():
    with tempfile.TemporaryDirectory(prefix="von-event-mode-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_runtime_event_mode_flag_set_ec940.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_runtime_event_mode_flag_set_ec940; fn.restype=Result; out=fn(); assert (out.continuation_address,out.flag_address,out.flag_value,out.return_target)==(0xec960,0x578514,1,0xec960); print("PASS: 0xec940 event mode flag setter")
if __name__=="__main__": main()
