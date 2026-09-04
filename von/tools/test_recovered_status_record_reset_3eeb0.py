#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_status_record_reset_3eeb0.c"

class Record(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "selector", "table_halfword", "helper_value", "caller_byte",
        "readback8", "readbackc", "readback10", "zero14", "zero18",
        "zero1c", "arg0")]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "status-record-reset.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_status_record_reset_3eeb0
    function.argtypes = [
        ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(ctypes.c_uint16),
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Record)]
    function.restype = ctypes.c_uint32

    status = (ctypes.c_uint16 * 23)(*[0] * 23)
    table = (ctypes.c_uint16 * 65536)()
    table[0x2345] = 0xbeef
    reads = (ctypes.c_uint32 * 3)(0x101, 0x202, 0x303)
    out = Record(*([0xffffffff] * 11))
    assert function(status, table, 0xabcdef01, 0x12345, 0x87654321,
                    reads, ctypes.byref(out)) == 23

    status[9] = 0x8000
    assert function(status, table, 0xabcdef01, 0x12345, 0x87654321,
                    reads, ctypes.byref(out)) == 9
    assert (out.selector, out.table_halfword, out.helper_value) == (0x2345, 0xbeef, 0x87654321)
    assert (out.caller_byte, out.arg0) == (0xef01, 0xabcdef01)
    assert (out.readback8, out.readbackc, out.readback10) == (0x101, 0x202, 0x303)
    assert (out.zero14, out.zero18, out.zero1c) == (0, 0, 0)

print("recovered status-record-reset 0x3eeb0 vectors: ok")
