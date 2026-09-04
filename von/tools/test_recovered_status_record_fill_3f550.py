#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_status_record_fill_3f550.c"


class Record(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "selector", "table_halfword", "arg0", "arg1", "arg2",
        "zero14", "zero18", "arg3", "arg4")]


def record_tuple(record):
    return tuple(getattr(record, name) for name, _ in Record._fields_)


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "status-record.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_status_record_fill_3f550
    function.argtypes = [
        ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(ctypes.c_uint16),
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Record),
        ctypes.POINTER(ctypes.c_uint32)]
    function.restype = ctypes.c_uint32

    status = (ctypes.c_uint16 * 23)(*[0] * 23)
    table = (ctypes.c_uint16 * 65536)()
    table[17] = 0x1234
    table[18] = 0xbeef
    out = Record(*([0xffffffff] * 9))
    units = ctypes.c_uint32(0xffffffff)

    # All occupied: the 0xcf allocation bound is reached after 23 slots.
    assert function(status, table, 0, 1, 2, 3, 4, 5,
                    ctypes.byref(out), ctypes.byref(units)) == 23
    assert units.value == 0xcf
    assert record_tuple(out) == (0xffffffff,) * 9

    # First available slot wins; nonzero flag selects 18 and preserves fields.
    status[7] = 0x8001
    assert function(status, table, 1, 0xabcdef01, 2, 3, 4, 5,
                    ctypes.byref(out), ctypes.byref(units)) == 7
    assert record_tuple(out) == (18, 0xbeef, 0xabcdef01, 2, 3, 0, 0, 4, 5)
    assert units.value == 7 * 9

    # Zero flag selects the alternate selector pair.
    status[7] = 0
    status[2] = 0x8000
    assert function(status, table, 0, 10, 11, 12, 13, 14,
                    ctypes.byref(out), ctypes.byref(units)) == 2
    assert record_tuple(out)[:2] == (17, 0x1234)

print("recovered status-record-fill 0x3f550 vectors: ok")
