#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_random_timing_prefix_840e8.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "helper_value", "status", "write_504e1c", "value_504e1c",
        "reaches_tail", "tail_504d8c", "tail_504d90")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_random_timing_prefix_840e8
    build.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32,
                      ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.c_uint32]
    build.restype = Plan

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Plan._fields_)

    assert values(5, -1, 0, 1, 0, 99, 7) == (0, 0xffffffff, 99, 1, 1, 0, 0, 0)
    assert values(5, 0, 2, 1, 4, 99, 7) == (3, 0, 33, 1, 1, 0, 0, 0)
    assert values(5, 5, 2, 1, 4, 99, 7) == (1, 5, 32, 1, 1, 0, 0, 0)
    assert values(5, 5, 2, 1, 2, 99, 7) == (2, 5, 37, 1, 1, 0, 0, 0)
    assert values(5, -1, 2, 1, 2, 99, 7) == (3, 0xffffffff, 33, 1, 1, 0, 0, 0)
    assert values(5, 3, 2, 1, 0, 0, 99, 7)[2] == 33
    assert values(4, 0, 2, 1, 4, 99, 7) == (3, 0, 33, 1, 1, 1, 7, 15)
    assert values(4, 1, 2, 1, 2, 99, 7) == (2, 1, 37, 1, 1, 1, 7, 15)
    assert values(4, 5, 2, 1, 4, 99, 7) == (1, 5, 32, 1, 1, 1, 7, 15)
    assert values(4, 0, 2, 3, 0, 99, 7)[2:] == (99, 1, 1, 1, 7, 15)

print("recovered 0x840e8 random-timing-prefix vectors: ok")
