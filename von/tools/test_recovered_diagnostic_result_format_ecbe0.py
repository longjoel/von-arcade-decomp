#!/usr/bin/env python3
import ctypes,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Result(ctypes.Structure): _fields_=[(n,ctypes.c_uint32) for n in ("entry_address","value_helper","renderer","format_string_address","selected_status_string","status_value","expected_value","has_expected_value")]
def main():
    with tempfile.TemporaryDirectory(prefix="von-diagnostic-format-") as d:
        so=Path(d)/"x.so"; subprocess.run([os.environ.get("CC","cc"),"-shared","-fPIC","-O2","-I",str(ROOT/"von/i960"),"-o",str(so),str(ROOT/"von/i960/recovered_diagnostic_result_format_ecbe0.c")],check=True)
        lib=ctypes.CDLL(str(so)); basic=lib.recovered_diagnostic_result_format_ecbe0; basic.argtypes=[ctypes.c_uint32]; basic.restype=Result
        for status,string in ((1,0xecbc0),(0,0xecbc8),(2,0xecbd0)):
            out=basic(status); assert (out.entry_address,out.value_helper,out.renderer,out.format_string_address,out.selected_status_string,out.has_expected_value)==(0xecbe0,0x1cac8,0xf5100,0xecbb8,string,0)
        compare=lib.recovered_diagnostic_result_format_compare_ecc40; compare.argtypes=[ctypes.c_uint32,ctypes.c_uint32]; compare.restype=Result
        for status,expected,string in ((0xffffffff,7,0xecbc8),(7,7,0xecbc0),(6,7,0xecc30)):
            out=compare(status,expected); assert (out.entry_address,out.selected_status_string,out.expected_value,out.has_expected_value)==(0xecc40,string,expected,1)
        print("PASS: 0xecbe0/ecc40 diagnostic result formatters")
if __name__=="__main__": main()
