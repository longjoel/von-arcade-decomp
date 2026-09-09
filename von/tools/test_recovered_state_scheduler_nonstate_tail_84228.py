#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_nonstate_tail_84228.c"


class Tail(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "write_504d80", "value_504d80", "write_504d8c", "value_504d8c",
        "write_504d90", "value_504d90")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-tail.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_nonstate_tail_84228
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    build.restype = Tail

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Tail._fields_)

    assert values(32, 0x12345678) == (1, 32, 1, 0x12345678, 1, 15)
    assert values(99, 0xffffffff) == (1, 99, 1, 0xffffffff, 1, 15)

print("recovered 0x84228 non-state tail vectors: ok")
