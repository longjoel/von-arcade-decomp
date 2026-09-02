#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_result_delta.c"
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "result-delta.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_geometry_result_reference_delta
    word3 = ctypes.POINTER(ctypes.c_uint32)
    function.argtypes = [word3, word3, word3]
    for references, responses in (((10, 20, 30), (1, 2, 3)),
                                  ((0, 0, 0), (1, 2, 0xffffffff)),
                                  ((0xffffffff, 0x80000000, 7), (1, 0x80000001, 9))):
        refs = (ctypes.c_uint32 * 3)(*references)
        values = (ctypes.c_uint32 * 3)(*responses)
        output = (ctypes.c_uint32 * 3)()
        function(refs, values, output)
        assert list(output) == [((r - v) & 0xffffffff) for r, v in zip(references, responses)]

print("recovered geometry result reference-minus-response vectors: ok")

copy = lib.recovered_geometry_result_delta_response_copy
copy.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint16)]
responses = (ctypes.c_uint32 * 2)(0x12345678, 0xFEDCBA98)
record = (ctypes.c_uint16 * 5)(*[0xA55A] * 5)
copy(responses, record)
assert list(record) == [0xA55A, 0xA55A, 0xA55A, 0x5678, 0xBA98]

print("recovered geometry result delta-response halfword placement: ok")
