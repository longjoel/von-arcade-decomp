#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure): _fields_=[(n,ctypes.c_uint32) for n in ("service_call","counter_before","counter_after","counter_address","return_target")]
def main():
    with tempfile.TemporaryDirectory(prefix="von-event-counter-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_runtime_event_counter_step_ec920.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_runtime_event_counter_step_ec920; fn.argtypes=[ctypes.c_uint32]; fn.restype=Result; out=fn(90)
        assert (out.service_call,out.counter_after,out.counter_address,out.return_target)==(0x28418,91,0x578510,0xec938); print("PASS: 0xec920 event counter step")
if __name__=="__main__": main()
