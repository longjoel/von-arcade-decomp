#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_clip_region.c"
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "clip-region.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_geometry_clip_region
    function.restype = ctypes.c_uint32
    function.argtypes = [ctypes.c_uint32] * 4
    values = range(-3, 4)
    for x in values:
        for y in values:
            for right in values:
                for bottom in values:
                    result = function(x & 0xffffffff, y & 0xffffffff,
                                      right & 0xffffffff, bottom & 0xffffffff)
                    if x == right or y == bottom:
                        expected = 4
                    elif x < right:
                        expected = 0 if y < bottom else 1
                    else:
                        expected = 2 if y < bottom else 3
                    assert result == expected

print("recovered geometry clip-region vectors: ok")
