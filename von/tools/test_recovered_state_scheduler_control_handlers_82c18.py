#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_control_handlers_82c18.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("route", "handled", "state_504d7c", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-control.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_control_handlers_82c18
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    build.restype = Plan

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Plan._fields_)

    for entry in (0x82C18, 0x82C28, 0x82C38):
        assert values(entry, 0, 4) == (0, 1, 7, 0)
        assert values(entry, 9, 4) == (1, 1, 4, 0x81E60)
    assert values(0x82C54, 0, 4) == (1, 1, 4, 0x81E60)
    assert values(0x82C54, 9, 7) == (1, 1, 7, 0x81E60)
    assert values(0x82C08, 0, 4) == (2, 0, 4, 0)

print("recovered 0x82c18 control-handler vectors: ok")
