#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_service_mod4_handlers_82df8.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("handled", "selector", "remainder_4")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "service-mod4.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_service_mod4_handlers_82df8
    build.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32]
    build.restype = Plan

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Plan._fields_)

    assert values(0x82DF8, 0, 0) == (1, 0, 0)
    assert values(0x82DF8, 7, 0) == (1, 3, 3)
    assert values(0x82DF8, -1, 0) == (1, -1 & 0xffffffff, -1 & 0xffffffff)
    assert values(0x82E0C, 4, 2) == (1, 4, 0)
    assert values(0x82E0C, 4, 3) == (1, 7, 0)
    assert values(0x82E0C, 7, 4) == (1, 7, 3)
    assert values(0x82E64, 4, 3) == (0, 0, 0)

print("recovered 0x82df8/0x82e0c mod4-handler vectors: ok")
