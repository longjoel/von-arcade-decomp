#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure): _fields_=[("hardware_word_address",ctypes.c_uint32),("hardware_word_before",ctypes.c_uint32),("hardware_word_after",ctypes.c_uint32),("hardware_mask",ctypes.c_uint32),("frequency_state_address",ctypes.c_uint32),("frequency_state_value",ctypes.c_uint32),("reset_call",ctypes.c_uint32),("geometry_table_build",ctypes.c_uint32),("service_reset_address",ctypes.c_uint32*9),("service_reset_count",ctypes.c_uint32),("mode_limit_address",ctypes.c_uint32),("mode_limit_value",ctypes.c_uint32),("mode_handler_call",ctypes.c_uint32),("exit_marker_address",ctypes.c_uint32),("exit_marker_value",ctypes.c_uint32),("host_call",ctypes.c_uint32),("frequency_address",ctypes.c_uint32),("frequency_before",ctypes.c_uint32),("frequency_after",ctypes.c_uint32),("return_target",ctypes.c_uint32)]
def main():
 with tempfile.TemporaryDirectory(prefix="von-startup-diagnostic-") as d:
  so=Path(d)/"x.so";subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_startup_diagnostic_state_seed_f3f00.c")],check=True);fn=ctypes.CDLL(str(so)).recovered_startup_diagnostic_state_seed_f3f00;fn.restype=Result;r=fn(0xffff,41);assert (r.hardware_word_after,r.service_reset_count,list(r.service_reset_address),r.mode_limit_value,r.exit_marker_value,r.frequency_after,r.return_target)==(0xfffe,9,[0x5784f8,0x578504,0x578500,0x578508,0x57850c,0x578510,0x578514,0x5785b4,0x5785b8],10,0x50,42,0xf3fb8);print("PASS: 0xf3f00 startup diagnostic-state seed")
if __name__=="__main__":main()
