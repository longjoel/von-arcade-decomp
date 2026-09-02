#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_record_init.c"
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "record-init.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_geometry_record_init
    function.argtypes = [
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    for empty in (0, 1):
        template = (ctypes.c_uint32 * 11)(*[0x1000 + i for i in range(11)])
        record = (ctypes.c_uint32 * 21)(*[0xffffffff] * 21)
        function(template, 0xabcdef01, empty, record)
        assert list(record[0:1]) == [0]
        assert list(record[1:5]) == [0x1000, 0x1001, 0x1002, 0x1003]
        assert record[5] == (999 if empty else 0xabcdef01)
        assert record[6] == 999
        assert list(record[7:12]) == [0, 0, 0, 0, 0]
        assert list(record[12:18]) == [0x1005, 0x1006, 0x1007, 0x1008, 0x1009, 0x100a]
        assert list(record[18:21]) == [0, 0, 0]

print("recovered geometry record-init vectors: ok")
