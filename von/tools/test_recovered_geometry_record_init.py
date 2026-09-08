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
        ctypes.POINTER(ctypes.c_ubyte),
    ]
    for empty in (0, 1):
        template = (ctypes.c_uint32 * 11)(*[0x1000 + i for i in range(11)])
        record = (ctypes.c_ubyte * 84)(*[0xff] * 84)
        function(template, 0xabcdef01, empty, record)
        def word(offset):
            return int.from_bytes(bytes(record[offset:offset + 4]), "little")
        def half(offset):
            return int.from_bytes(bytes(record[offset:offset + 2]), "little")

        assert word(0x00) == 0
        assert [word(offset) for offset in (0x04, 0x08, 0x0c, 0x10)] == [
            0x1000, 0x1001, 0x1002, 0x1003]
        assert word(0x14) == (999 if empty else 0xabcdef01)
        assert word(0x18) == 999
        assert all(word(offset) == 0 for offset in (0x1c, 0x20, 0x24, 0x28, 0x2c))
        assert [word(offset) for offset in (0x30, 0x34, 0x38)] == [
            0x1004, 0x1005, 0x1006]
        assert word(0x3c) == 0x10081007
        assert half(0x3e) == 0x1008
        assert word(0x40) == 0x1009
        assert word(0x44) == 0x100a
        assert all(word(offset) == 0 for offset in (0x48, 0x4c, 0x50))

print("recovered geometry record-init vectors: ok")
