#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_status_record_seed_3f4e8.c"


class Record(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "selector", "table_halfword", "helper_value", "caller_field",
        "caller_value")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "status-record.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_status_record_seed_3f4e8
    function.argtypes = [
        ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(ctypes.c_uint16),
        ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Record)]
    function.restype = ctypes.c_uint32

    status = (ctypes.c_uint16 * 23)(*[0] * 23)
    table = (ctypes.c_uint16 * 65536)()
    table[10] = 0xbeef
    out = Record(*([0xffffffff] * 5))

    # No negative status means the bounded scan returns 23 and does not write.
    assert function(status, table, 0x12345678, 0xabcdef01,
                    ctypes.byref(out)) == 23
    assert (out.selector, out.table_halfword, out.helper_value,
            out.caller_field, out.caller_value) == (0xffffffff,) * 5

    # Bit 15 is the free-slot marker after ldis sign extension; the first
    # matching slot wins and the halfword stores retain their low 16 bits.
    status[7] = 0x8001
    status[12] = 0xffff
    assert function(status, table, 0x12345678, 0xabcdef01,
                    ctypes.byref(out)) == 7
    assert (out.selector, out.table_halfword, out.helper_value,
            out.caller_field, out.caller_value) == (10, 0xbeef, 0, 0x5678,
                                                     0xabcdef01)

print("recovered status-record-seed 0x3f4e8 vectors: ok")
