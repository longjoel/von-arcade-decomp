#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_service_call_82c60.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("argument", "target", "tail_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-service.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_service_call_82c60
    build.argtypes = [ctypes.c_uint32]
    build.restype = Plan
    result = build(0x12345678)
    assert (result.argument, result.target, result.tail_target) == \
        (0x12345678, 0x840B0, 0x82D74)

print("recovered 0x82c60 service-call vector: ok")
