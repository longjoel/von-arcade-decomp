#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
 _fields_=[("result_state_address",ctypes.c_uint32),("result_state_before",ctypes.c_uint32),("result_state_after",ctypes.c_uint32),("initialization_performed",ctypes.c_uint32),("statistics_state_address",ctypes.c_uint32),("statistics_state_before",ctypes.c_uint32),("alternate_path",ctypes.c_uint32),("header_x",ctypes.c_uint32),("header_y",ctypes.c_uint32),("header_string",ctypes.c_uint32),("header_renderer",ctypes.c_uint32),("row_count",ctypes.c_uint32),("row_x",ctypes.c_uint32*6),("row_y",ctypes.c_uint32*6),("row_value_address",ctypes.c_uint32*6),("row_string",ctypes.c_uint32*6),("return_target",ctypes.c_uint32),("alternate_target",ctypes.c_uint32)]
def main():
 with tempfile.TemporaryDirectory(prefix="von-game-time-entry-") as d:
  so=Path(d)/"x.so";subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_game_time_statistics_entry_f33a0.c")],check=True);fn=ctypes.CDLL(str(so)).recovered_diagnostic_game_time_statistics_entry_f33a0;fn.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(Result)];out=Result();fn(0,0,ctypes.byref(out));assert (out.result_state_after,out.header_x,out.header_y,out.header_string,out.row_count,list(out.row_y),list(out.row_value_address),out.return_target)==(1,18,6,0xf2ef0,6,[11,12,16,17,18,19],[0x1d00040,0x1d00044,0x1d00048,0x1d0003c,0x1d00048,0x1d0004c],0xf3a3c);fn(1,1,ctypes.byref(out));assert (out.initialization_performed,out.alternate_path,out.alternate_target)==(0,1,0xf3668);print("PASS: 0xf33a0 game-time statistics entry")
if __name__=="__main__":main()
