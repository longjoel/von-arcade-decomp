#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_status_record_init_3ecd0.c"

class Record(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "selector", "table_halfword", "helper_value", "caller_byte",
        "arg0", "arg1", "arg2", "zero14", "zero18", "zero1c", "arg3")]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "status-record.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_status_record_init_3ecd0
    function.argtypes = [
        ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(ctypes.c_uint16),
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Record)]
    function.restype = ctypes.c_uint32

    status = (ctypes.c_uint16 * 23)(*[0] * 23)
    table = (ctypes.c_uint16 * 65536)()
    table[0x2345] = 0xbeef
    out = Record(*([0xffffffff] * 11))
    assert function(status, table, 0x123456789, 0xabcdef01, 2, 3, 4, 5, ctypes.byref(out)) == 23

    status[4] = 0x8001
    assert function(status, table, 0x12345, 0xabcdef01, 2, 3, 4, 5, ctypes.byref(out)) == 4
    assert (out.selector, out.table_halfword, out.helper_value) == (0x12345, 0xbeef, 5)
    assert (out.caller_byte, out.arg0, out.arg1, out.arg2, out.arg3) == (1, 0xabcdef01, 2, 3, 4)
    assert (out.zero14, out.zero18, out.zero1c) == (0, 0, 0)

    table[0x2345] = 0xbeef
    assert function(status, table, 0x12345, 0x101, 2, 3, 4, 5, ctypes.byref(out)) == 4
    assert out.table_halfword == 0xbeef

print("recovered status-record-init 0x3ecd0 vectors: ok")
