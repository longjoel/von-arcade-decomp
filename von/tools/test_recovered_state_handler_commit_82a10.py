#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_handler_commit_82a10.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "entered", "action", "stores", "marker_504db4", "marker_504db8",
        "action_504d98")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "handler-commit.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_handler_commit_82a10
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.c_uint32, ctypes.c_uint32]
    build.restype = Plan

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Plan._fields_)

    assert values(0, 30, 3, 4) == (0, 0, 0, 0, 0, 0)
    assert values(1, 13, 0, 0) == (1, 6, 1, 0xffffffff, 20, 6)
    assert values(1, 16, 1, 0) == (1, 16, 1, 0xffffffff, 20, 16)
    assert values(1, 29, 1, 0) == (1, 17, 1, 0xffffffff, 20, 17)
    assert values(1, 30, 1, 0) == (1, 18, 1, 0xffffffff, 20, 18)
    assert values(1, 31, 1, 0) == (1, 16, 1, 0xffffffff, 20, 16)
    assert values(1, 32, 1, 0) == (1, 16, 1, 0xffffffff, 20, 16)
    assert values(1, 18, 3, 4) == (1, 16, 1, 0xffffffff, 20, 16)
    assert values(1, 18, 3, 12) == (1, 16, 1, 0xffffffff, 20, 16)

print("recovered 0x82a10 status-commit vectors: ok")
