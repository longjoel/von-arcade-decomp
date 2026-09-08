#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_profile_table_loader.c"

class Record(ctypes.Structure):
    _fields_ = [(f"word{index}", ctypes.c_uint32) for index in range(6)]

class Output(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "published_pair_low", "published_pair_high", "published_word",
        "fifo_selector", "fifo_record_word")]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "profile-loader.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_geometry_profile_table_loader
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Record), ctypes.POINTER(Output)]
    function.restype = None

    table = (Record * 3)(
        Record(0x1000, 0x1001, 0x1002, 0x1003, 0x1004, 0x1005),
        Record(0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005),
        Record(0x3000, 0x3001, 0x3002, 0x3003, 0x3004, 0x3005),
    )
    for index, selector in ((0, 0), (1, 3), (2, 0x80)):
        output = Output()
        function(index, selector, table, ctypes.byref(output))
        record = table[index]
        assert output.published_pair_low == record.word0
        assert output.published_pair_high == record.word1
        assert output.published_word == record.word3
        assert output.fifo_selector == selector | 0x40
        assert output.fifo_record_word == record.word5

print("PASS: shared 0x6f900/0x6f970 profile-table loader core")
