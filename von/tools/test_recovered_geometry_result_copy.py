#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_result_copy.c"
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "result-copy.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_geometry_result_copy
    function.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    for responses in ((0, 1, 2), (0xffffffff, 0x80000000, 7)):
        source_values = (ctypes.c_uint32 * 3)(*responses)
        left = (ctypes.c_uint32 * 7)(*[0xa5a5a5a5] * 7)
        right = (ctypes.c_uint32 * 7)(*[0x5a5a5a5a] * 7)
        function(source_values, left, right)
        assert list(left[:3]) == list(responses)
        assert list(right[4:7]) == list(responses)
        assert list(left[3:]) == [0xa5a5a5a5] * 4
        assert list(right[:4]) == [0x5a5a5a5a] * 4

print("recovered geometry result-copy vectors: ok")
