#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_reject_82d68.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "input_value_504d80", "rejected_value_504d80", "destination",
        "tail_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-reject.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_reject_82d68
    build.argtypes = [ctypes.c_uint32]
    build.restype = Plan

    for value in (0, 1, 7, 9, 0xffffffff):
        result = build(value)
        assert (result.input_value_504d80, result.rejected_value_504d80,
                result.destination, result.tail_target) == (value, 8, 0x504D80, 0x82D74)

print("recovered 0x82d68 scheduler-reject vectors: ok")
