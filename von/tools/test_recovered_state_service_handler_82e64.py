#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_service_handler_82e64.c"


class Plan(ctypes.Structure):
    _fields_ = [("admitted", ctypes.c_uint32),
                ("downstream_value", ctypes.c_uint32),
                ("remainder_7", ctypes.c_int32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "service-82e64.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_service_handler_82e64
    build.argtypes = [ctypes.c_int32, ctypes.c_uint32]
    build.restype = Plan

    for state in (0, 1, 5, 6):
        result = build(4, state)
        assert (result.admitted, result.downstream_value,
                result.remainder_7) == (1, 2, 4)
    assert build(4, 3).admitted == 0
    assert build(6, 5).admitted == 1
    assert build(5, 5).admitted == 0
    assert build(-1, 0).admitted == 0

print("recovered 0x82e64 service-handler vectors: ok")
