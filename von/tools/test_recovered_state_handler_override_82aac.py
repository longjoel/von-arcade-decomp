#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_handler_override_82aac.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("applied", "action", "action_504d98", "marker_504db8")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "handler-override.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_handler_override_82aac
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    build.restype = Plan

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Plan._fields_)

    assert values(2, 4) == (0, 0, 0, 0)
    assert values(3, 0) == (0, 0, 0, 0)
    assert values(3, 4) == (1, 6, 6, 20)
    assert values(3, 12) == (0, 0, 0, 0)
    assert values(3, 28) == (0, 0, 0, 0)

print("recovered 0x82aac handler-override vectors: ok")
