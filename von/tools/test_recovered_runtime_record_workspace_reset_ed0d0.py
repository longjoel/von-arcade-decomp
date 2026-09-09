#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure): _fields_=[("result_slot_address",ctypes.c_uint32*6),("result_slot_value",ctypes.c_uint32*6),("primary_slot_address",ctypes.c_uint32*6),("alternate_slot_address",ctypes.c_uint32*4),("parallel_slot_address",ctypes.c_uint32*13),("continuation_address",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
    with tempfile.TemporaryDirectory(prefix="von-workspace-reset-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_runtime_record_workspace_reset_ed0d0.c")],check=True)
        fn=ctypes.CDLL(str(so)).recovered_runtime_record_workspace_reset_ed0d0; fn.restype=Result; out=fn()
        assert list(out.result_slot_address)==[0x578530,0x578534,0x578538,0x57853c,0x578540,0x578544]; assert list(out.result_slot_value)==[0xffffffff]*6
        assert list(out.primary_slot_address)==[0x578548,0x57854c,0x578550,0x578554,0x578558,0x57855c]; assert list(out.alternate_slot_address)==[0x578560,0x578564,0x578568,0x57856c]
        assert list(out.parallel_slot_address)==[0x578570,0x578574,0x578578,0x57857c,0x578580,0x578584,0x578588,0x57858c,0x578590,0x578594,0x578598,0x57859c,0x5785a0]; assert (out.continuation_address,out.return_target)==(0xed1d0,0xed1cc)
        print("PASS: 0xed0d0 runtime workspace reset")
if __name__=="__main__": main()
