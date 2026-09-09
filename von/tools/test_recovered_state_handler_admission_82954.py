#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_handler_admission_82954.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("route", "target", "status")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "handler-admission.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_handler_admission_82954
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32,
                      ctypes.c_int32]
    build.restype = Plan

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Plan._fields_)

    override = (0, 0x82AAC, 29)
    commit = (1, 0x82A10, 29)
    assert values(29, 1 << 3, 1, 0, 1, 0, 0) == commit
    assert values(29, 1 << 3, 0, 0, 1, 0, 0) == override
    assert values(29, 1 << 2, 1, 0, 1, 0, 0) == override
    assert values(30, 1 << 4, 1, 0, 1, 0, 0) == (1, 0x82A10, 30)
    assert values(31, 1 << 5, 1, 0, 1, 0, 0) == (1, 0x82A10, 31)
    assert values(32, 0xffffffff, 1, 0, 1, 0, 0) == (0, 0x82AAC, 32)
    assert values(13, 0, 1, 6, -1, 4, 5) == (1, 0x82A10, 13)
    assert values(14, 0, 1, 6, -1, 5, 5) == (0, 0x82AAC, 14)
    assert values(15, 0, 1, 5, -1, 4, 5) == (0, 0x82AAC, 15)
    assert values(13, 0, 1, 6, 0, 4, 5) == (0, 0x82AAC, 13)

print("recovered 0x82954 handler-admission vectors: ok")
